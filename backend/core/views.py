import Levenshtein
from datetime import datetime
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.throttling import AnonRateThrottle
from django.http import JsonResponse
from core.models import (
    Homepage, InfoMeeting, AirportTransfer, Question, 
    ContactInfo, AboutUs, Excursion, TransferSchedule, Hotel,
    PageBanner, Hotel, PickupPoint, TransferNotification,
    TransferInquiry, TransferScheduleItem, TransferScheduleGroup,
    PrivacyPolicy, InfoMeetingScheduleItem, ExcursionRegionPrice,
    PageBanner, ExcursionPickupPoint, Question, TeamMember, TransferPageContentBlock
    )
from core.utils import send_html_email, send_question_notification
from .serializers import (
    HomepageSerializer, InfoMeetingSerializer, AirportTransferSerializer,
    QuestionSerializer, ContactInfoSerializer, AboutUsSerializer, ExcursionSerializer,
    TransferScheduleRequestSerializer, TransferScheduleResponseSerializer,
    HotelSerializer, SimpleHotelSerializer, TransferNotificationCreateSerializer,
    TransferInquirySerializer, PrivacyPolicySerializer, InfoMeetingScheduleItemSerializer,
    PageBannerSerializer, ExcursionDetailSerializer, QuestionSerializer, TeamMemberSerializer,
    TransferPageContentBlockSerializer
    )
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import admin
from django.conf import settings

from django.urls import path
from django.utils.translation import activate, get_language, gettext as _
from django.shortcuts import render, redirect
from .forms import BulkTransferScheduleForm
from .models import Hotel, TransferSchedule

from django.template.loader import render_to_string


from rest_framework.decorators import api_view
from rest_framework.response import Response
from Levenshtein import distance as levenshtein_distance
from .models import TransferScheduleGroup, TransferSchedule, PickupPoint, Hotel
from .throttling import ContactFormThrottle  # если у тебя оттуда
from .utils import send_question_notification
import logging

logger = logging.getLogger(__name__)

# Главное правило: RetrieveAPIView + queryset + serializer_class

# Получение баннеров на страницах
def page_banner_api(request, page):
    try:
        banner = PageBanner.objects.get(page=page)
        data = {
            "image": banner.image.url if banner.image else "",
            "titles": {
                "ru": banner.title_ru,
                "en": banner.title_en,
                "es": banner.title_es,
                "uk": banner.title_uk,
                "et": banner.title_et,
                "lv": banner.title_lv,
                "lt": banner.title_lt,
            }
        }
        return JsonResponse(data)
    except PageBanner.DoesNotExist:
        return JsonResponse({"error": "Banner not found"}, status=404)

class PageBannerView(RetrieveAPIView):
    serializer_class = PageBannerSerializer
    lookup_field = "page"

    def get_object(self):
        page = self.kwargs.get("page")
        return PageBanner.objects.filter(page=page).first()

class HomepageView(RetrieveAPIView):
    queryset = Homepage.objects.all()
    serializer_class = HomepageSerializer

    def get_object(self):
        return self.queryset.first()

class InfoMeetingView(RetrieveAPIView):
    queryset = InfoMeeting.objects.all()
    serializer_class = InfoMeetingSerializer

    def get_object(self):
        return self.queryset.first()

from django.utils.timezone import now

@api_view(['GET'])
def info_meeting_schedule(request):
    hotel_id = request.query_params.get('hotel_id')
    if not hotel_id:
        return Response({"error": "hotel_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

    today = now().date()  # сегодняшняя дата

    schedule_items = InfoMeetingScheduleItem.objects.filter(
        hotel=hotel,
        date__gte=today  # 🔹 только даты сегодня и позже
    ).order_by('date', 'time_from')

    serializer = InfoMeetingScheduleItemSerializer(schedule_items, many=True)

    return Response({
        "hotel": hotel.name,
        "schedule": serializer.data
    })



# Трансферы
class AirportTransferView(RetrieveAPIView):
    queryset = AirportTransfer.objects.all()
    serializer_class = AirportTransferSerializer

    def get_object(self):
        return self.queryset.first()

class TransferContentListAPIView(generics.ListAPIView):
    serializer_class = TransferPageContentBlockSerializer

    def get_queryset(self):
        page = self.kwargs.get('page')
        return (TransferPageContentBlock.objects
                .filter(page=page, is_active=True)
                .order_by('order','id'))

# Массовое добавление времени на трансферы
class BulkTransferScheduleAdmin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("mass-transfer-schedule/", self.admin_site.admin_view(self.bulk_transfer_schedule), name="mass_transfer_schedule")
        ]
        return my_urls + urls

    def bulk_transfer_schedule(self, request):
        if request.method == 'POST':
            form = BulkTransferScheduleForm(request.POST)
            if form.is_valid():
                transfer_type = form.cleaned_data['transfer_type']
                transfer_date = form.cleaned_data['transfer_date']

                for hotel in Hotel.objects.all():
                    time_field = f"time_{hotel.id}"
                    point_field = f"pickup_{hotel.id}"
                    lastname_field = f"lastname_{hotel.id}"  # 🟡 Новое поле

                    time = form.cleaned_data.get(time_field)
                    point = form.cleaned_data.get(point_field)
                    last_name = form.cleaned_data.get(lastname_field)  # 🟡 Получаем фамилию

                    if time and point:
                        TransferSchedule.objects.create(
                            transfer_type=transfer_type,
                            date=transfer_date,
                            hotel=hotel,
                            pickup_point=point,
                            departure_time=time,
                            passenger_last_name=last_name.strip() if last_name else None  # ✅ Сохраняем фамилию
                        )

                self.message_user(request, "Расписание успешно добавлено!")
                return redirect("..")
        else:
            form = BulkTransferScheduleForm()

        return render(request, "admin/bulk_transfer_schedule.html", {
            "form": form,
            "title": "Массовое добавление расписания трансферов",
        })

class TransferScheduleLookupView(APIView):
    def post(self, request):
        serializer = TransferScheduleRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            transfer_type = data['transfer_type']
            hotel_id = data['hotel_id']
            departure_date = data['departure_date']
            last_name = data.get('passenger_last_name', '').strip().lower()

            qs = TransferSchedule.objects.filter(
                transfer_type=transfer_type,
                hotel_id=hotel_id,
                departure_date=departure_date
            )

            if transfer_type == 'private' and last_name:
                qs = qs.filter(passenger_last_name__iexact=last_name)

            transfer = qs.first()
            if not transfer:
                return Response({'error': 'Трансфер не найден'}, status=404)

            response = {
                'departure_time': transfer.departure_time,
                'pickup_point_name': transfer.pickup_point.name if transfer.pickup_point else '',
                'pickup_point_lat': transfer.pickup_point.latitude if transfer.pickup_point else None,
                'pickup_point_lng': transfer.pickup_point.longitude if transfer.pickup_point else None,
                'hotel_lat': transfer.hotel.latitude,
                'hotel_lng': transfer.hotel.longitude,
            }

            return Response(response, status=200)

        return Response(serializer.errors, status=400)

# Вывод информации о трансфере для туриста
@api_view(['GET'])
def transfer_info(request):
    hotel_id = request.GET.get('hotel_id')
    date = request.GET.get('date')

    if not hotel_id or not date:
        return Response({"error": "Missing hotel_id or date"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        schedule = TransferSchedule.objects.get(hotel_id=hotel_id, departure_date=date)
        pickup = schedule.pickup_point
        return Response({
            "departure_time": schedule.departure_time.strftime("%H:%M"),
            "pickup_point": {
                "name": pickup.name if pickup else "—",
                "latitude": pickup.latitude if pickup else None,
                "longitude": pickup.longitude if pickup else None,
            }
        })
    except TransferSchedule.DoesNotExist:
        return Response({"error": "No transfer found for given hotel and date"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def transfer_schedule_view(request):
    hotel_id = request.GET.get('hotel_id')
    date = request.GET.get('date')
    transfer_type = request.GET.get('type', 'group')
    last_name = request.GET.get('last_name', '').strip().lower()

    if not hotel_id or not date:
        return Response({"error": "Missing hotel_id or date"}, status=400)

    try:
        group = TransferScheduleGroup.objects.filter(
            date=date,
            transfer_type=transfer_type
        ).first()

        if not group:
            return Response({'error': 'No transfer group found'}, status=404)

        schedules = group.schedules.filter(hotel_id=hotel_id).order_by('departure_time')

        if not schedules.exists():
            return Response({'error': 'No transfer schedule found'}, status=404)

        # === PRIVATE TRANSFER ===
        if transfer_type == 'private':
            if not last_name:
                return Response({
                    "success": False,
                    "reason": "need_last_name",
                    "message": "Укажите фамилию для получения информации о трансфере."
                }, status=200)

            # === Точное совпадение ===
            exact = schedules.filter(passenger_last_name__iexact=last_name).first()
            if exact:
                pp = exact.pickup_point or PickupPoint.objects.filter(
                    hotel=exact.hotel,
                    transfer_type='private'
                ).first()
                return Response({
                    "success": True,
                    "pickup_time": exact.departure_time.strftime("%H:%M"),
                    "pickup_point": pp.name if pp else "—",
                    "pickup_lat": pp.latitude if pp else None,
                    "pickup_lng": pp.longitude if pp else None,
                })

            # === Fuzzy поиск по фамилии ===
            candidates = []
            for ln in schedules.values_list('passenger_last_name', flat=True):
                if ln:
                    dist = levenshtein_distance(last_name, ln.lower())
                    if 0 < dist <= 3:
                        candidates.append((dist, ln))
            if candidates:
                candidates.sort()
                return Response({
                    "success": False,
                    "reason": "no_exact_match",
                    "suggestion": candidates[0][1]
                })

            # === Фамилия не найдена ===
            return Response({
                "success": False,
                "reason": "not_found",
                "message": "Фамилия не найдена. Проверьте правильность написания."
            })


            if schedules.count() > 1:
                return Response({
                    "success": False,
                    "reason": "multiple_transfers",
                    "message": "Из этого отеля выезжает несколько семей. Укажите фамилию."
                })

            ts = schedules.first()
            pp = ts.pickup_point or PickupPoint.objects.filter(
                hotel=ts.hotel,
                transfer_type='private'
            ).first()
            latitude = pp.latitude if pp else ts.hotel.latitude
            longitude = pp.longitude if pp else ts.hotel.longitude
            pickup_name = pp.name if pp else ts.hotel.name
            return Response({
                "success": True,
                "pickup_time": ts.departure_time.strftime("%H:%M"),
                "pickup_point": pickup_name,
                "pickup_lat": latitude,
                "pickup_lng": longitude,
            })

        # === GROUP TRANSFER ===
        else:
            # Найдём хотя бы один трансфер
            ts = schedules.first()

            # Если у него нет явно заданной pickup_point — ищем по отелю
            pp = ts.pickup_point if ts and ts.pickup_point else PickupPoint.objects.filter(hotel_id=hotel_id, transfer_type='group').first()

            return Response({
                "pickup_time": ts.departure_time.strftime("%H:%M") if ts else None,
                "pickup_point": pp.name if pp else "—",
                "pickup_lat": pp.latitude if pp else None,
                "pickup_lng": pp.longitude if pp else None,
            })


    except Exception as e:
        return Response({"error": str(e)}, status=500)





@api_view(['GET'])
def available_hotels_for_transfer(request):
    date_str = request.GET.get('date')
    transfer_type = request.GET.get('type', 'group')  # default = group

    if not date_str:
        return Response({"error": "Missing date parameter"}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    hotel_ids = TransferSchedule.objects.filter(
        departure_date=date,
        transfer_type=transfer_type
    ).values_list('hotel_id', flat=True).distinct()

    hotels = Hotel.objects.filter(id__in=hotel_ids)
    serializer = SimpleHotelSerializer(hotels, many=True)
    return Response(serializer.data)


class TransferNotificationViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TransferNotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            group = TransferScheduleGroup.objects.filter(
                date=instance.departure_date,
                transfer_type__iexact=instance.transfer_type
            ).first()

            transfer_item = None
            pickup_point = None

            if group:
                schedules = TransferSchedule.objects.filter(
                    group=group,
                    hotel=instance.hotel
                )

                if instance.transfer_type == 'private':
                    # ⛔ Обязательно указание фамилии
                    if not instance.last_name:
                        return Response({
                            "detail": "Для индивидуального трансфера требуется указать фамилию.",
                            "status": "missing_last_name"
                        }, status=400)

                    # 🔍 Печать всех фамилий в расписании для отладки
                    print("== ВСЕ ФАМИЛИИ В БАЗЕ ==")
                    for s in schedules:
                        print(f"[БД]: '{s.passenger_last_name.strip().lower()}'")

                    print(f"[ИЩЕМ]: '{instance.last_name.strip().lower()}'")

                    # 🔍 Пытаемся найти по фамилии
                    transfer_item = schedules.filter(
                        passenger_last_name__iexact=instance.last_name.strip()
                    ).first()

                    if not transfer_item:
                        return Response({
                            "detail": "Фамилия не найдена в списке трансферов на эту дату.",
                            "status": "not_found"
                        }, status=404)

                else:
                    # ✅ Групповой трансфер — фамилия не обязательна
                    transfer_item = schedules.order_by("departure_time").first()

                # 📍 Точка сбора
                if transfer_item and transfer_item.pickup_point:
                    pickup_point = transfer_item.pickup_point
                else:
                    pickup_point = PickupPoint.objects.filter(
                        hotel=instance.hotel,
                        transfer_type=instance.transfer_type
                    ).first()

            # 🕒 Время трансфера
            departure_time = transfer_item.departure_time if transfer_item else None
            departure_time_str = departure_time.strftime('%H:%M') if departure_time else _("—")

            # 📌 Название и карта
            pickup_name = pickup_point.name if pickup_point else _("не указана")
            map_link = (
                f"https://www.google.com/maps?q={pickup_point.latitude},{pickup_point.longitude}"
                if pickup_point and pickup_point.latitude and pickup_point.longitude
                else None
            )

            # 🌍 Устанавливаем язык
            activate(instance.language)

            # ✉️ Отправка письма
            send_html_email(
                subject="Airport transfer details",
                to_email=instance.email,
                template_name=f"emails/transfer_notification_{instance.language}.html",
                context={
                    "hotel_name": instance.hotel.name,
                    "departure_date": instance.departure_date.strftime('%d.%m.%Y'),
                    "departure_time": departure_time_str,
                    "pickup_point": pickup_name,
                    "map_link": map_link,
                }
            )

            # 💾 Лог отправки
            if departure_time:
                instance.departure_time_sent = departure_time
                instance.save(update_fields=["departure_time_sent"])

            return Response({"detail": _("Информация отправлена на почту.")}, status=201)

        return Response(serializer.errors, status=400)


@api_view(['GET'])
def confirm_transfer_notification(request, token):
    try:
        notif = TransferNotification.objects.get(confirmation_token=token)
        notif.is_confirmed = True
        notif.save()
        return render(request, 'confirmation_success.html')  # HTML-шаблон
    except TransferNotification.DoesNotExist:
        return render(request, 'confirmation_error.html')  # HTML-шаблон с ошибкой


@api_view(['POST'])
def notify_transfer_change(request):
    serializer = TransferNotificationCreateSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        send_transfer_update_email(instance)
        return Response({"detail": _("Письмо отправлено с просьбой подтвердить.")})
    return Response(serializer.errors, status=400)

        
# Вьюшка обратной связи по индивидуальтным трансферам
class TransferInquiryViewSet(viewsets.ModelViewSet):
    queryset = TransferInquiry.objects.all()
    serializer_class = TransferInquirySerializer
    http_method_names = ['post']  # только POST для внешнего доступа

    def perform_create(self, serializer):
        inquiry = serializer.save()

        # === Определяем язык письма ===
        supported_languages = ['ru', 'en', 'es', 'lv', 'lt', 'et', 'uk']
        lang = inquiry.language if inquiry.language in supported_languages else 'ru'
        template_name = f"emails/transfer_reply_{lang}.html"

        # === Контекст шаблона ===
        context = {
            'name': inquiry.last_name,
            'hotel': inquiry.hotel.name if inquiry.hotel else '—',
            'date': inquiry.departure_date,
            'flight': inquiry.flight_number or '—',
            'reply': '',  # или текст по умолчанию, если нужно
        }

        html_content = render_to_string(template_name, context)
        text_content = (
            f"Уважаемый(ая) {inquiry.last_name},\n\n"
            f"Мы получили ваш запрос по трансферу.\n"
            f"Дата: {inquiry.departure_date}\n"
            f"Отель: {inquiry.hotel.name if inquiry.hotel else '—'}\n"
            f"Номер рейса: {inquiry.flight_number or '—'}\n\n"
            f"Мы свяжемся с вами в ближайшее время."
        )

        # === Отправка письма ===
        email = EmailMultiAlternatives(
            subject="Your request has been accepted",
            body=text_content,
            from_email="CostaSolinfo.Malaga@gmail.com",
            to=[inquiry.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


# class QuestionView(RetrieveAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer

#     def get_object(self):
#         return self.queryset.first()

class ContactFormThrottle(AnonRateThrottle):
    rate = '5/min'  # простая защита от спама

class QuestionCreateAPIView(APIView):
    throttle_classes = [ContactFormThrottle]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def post(self, request, *args, **kwargs):
        handler_signature = "QuestionCreateAPIView-vFinal"

        # 0) берём входящие данные (делаем обычный dict)
        try:
            incoming = request.data
            data = dict(incoming)  # DRF Request.data обычно уже dict
        except Exception:
            # на всякий случай
            data = request.data.copy()

        # 1) язык
        language = (data.get("language") or request.headers.get("Accept-Language") or "ru")[:5]
        data["language"] = language

        # 2) источник (если фронт не прислал)
        data.setdefault("source", "contacts" if "contact-questions" in request.path else "ask")

        # 3) категория
        if data.get("category") not in dict(Question.CATEGORY_CHOICES):
            data["category"] = "other"

        logger.debug("[QuestionCreateAPIView] incoming path=%r content_type=%r data=%r",
                     request.path, request.content_type, incoming)

        if settings.DEBUG and request.GET.get('debug') == '1':
            return Response({
                "handler": handler_signature,
                "incoming": incoming,
                "normalized": data
            }, status=200)

        # 4) сериализация и сохранение
        serializer = QuestionSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        logger.debug("[QuestionCreateAPIView] validated_data=%r", serializer.validated_data)

        obj = serializer.save()
        obj.refresh_from_db(fields=['question', 'language', 'source'])
        logger.debug("[QuestionCreateAPIView] AFTER SAVE: id=%s, source=%s, lang=%s, question=%r",
                     obj.id, obj.source, obj.language, obj.question)

        # 5) страховка: фиксируем оригинал и проверим, не стерлось ли после уведомления
        _orig_q = obj.question

        try:
            send_question_notification(obj, language)  # ВАЖНО: внутри ничего не должно присваивать obj.question
        except Exception as e:
            logger.exception("send_question_notification failed: %s", e)

        # 6) проверка после отправки письма — не стерли ли поле
        obj.refresh_from_db(fields=['question'])
        if (not obj.question) and _orig_q:
            logger.warning("[QuestionCreateAPIView] question cleared during notification; restoring. id=%s", obj.id)
            Question.objects.filter(id=obj.id).update(question=_orig_q)
            obj.question = _orig_q

        return Response({
            "message": "Вопрос успешно отправлен.",
            "id": obj.id,
            "saved_question": obj.question,   # то, что реально лежит в БД
        }, status=status.HTTP_201_CREATED)




class ContactInfoView(RetrieveAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer

    def get_object(self):
        return self.queryset.first()

class AboutUsView(RetrieveAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

    def get_object(self):
        return self.queryset.first()

class TeamMemberListAPIView(ListAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer

class ExcursionView(RetrieveAPIView):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionSerializer

    def get_object(self):
        return self.queryset.first()  # если только одна экскурсия, иначе делаем ListAPIView

def get_excursion_price(request):
    excursion_id = request.GET.get("excursion")
    hotel_id = request.GET.get("hotel")

    try:
        hotel = Hotel.objects.get(id=hotel_id)
        region = hotel.region
        price = ExcursionRegionPrice.objects.get(excursion_id=excursion_id, region=region)
        return JsonResponse({
            "price_adult": str(price.price_adult),
            "price_child": str(price.price_child),
        })
    except (Hotel.DoesNotExist, ExcursionRegionPrice.DoesNotExist):
        return JsonResponse({"error": "Цена не найдена"}, status=404)

class ExcursionListView(ListAPIView):
    queryset = Excursion.objects.filter(is_active=True)
    serializer_class = ExcursionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ExcursionDetailView(RetrieveAPIView):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionDetailSerializer

def pickup_point_detail(request, pk):
    pickup = get_object_or_404(ExcursionPickupPoint, pk=pk)
    return JsonResponse({
        "id": pickup.id,
        "pickup_point_name": pickup.pickup_point_name,
        "latitude": str(pickup.latitude) if pickup.latitude else None,
        "longitude": str(pickup.longitude) if pickup.longitude else None,
        "pickup_time": pickup.pickup_time.strftime("%H:%M") if pickup.pickup_time else None,
    })

@api_view(['GET'])
def excursion_pickup_view(request, excursion_id):
    hotel_id = request.GET.get("hotel_id")
    if not hotel_id:
        return Response({"error": "hotel_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pickup = ExcursionPickupPoint.objects.get(excursion_id=excursion_id, hotel_id=hotel_id)
    except ExcursionPickupPoint.DoesNotExist:
        return Response({"error": "Pickup point not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "id": pickup.id,
        "name": pickup.pickup_point_name,
        "lat": float(pickup.latitude) if pickup.latitude else None,
        "lng": float(pickup.longitude) if pickup.longitude else None,
        "time": pickup.pickup_time.strftime("%H:%M") if pickup.pickup_time else None,
        "price_adult": pickup.price_adult,
        "price_child": pickup.price_child,
    })

# Поисковая система по отелям
@api_view(['GET'])
def hotel_search(request):
    search = request.GET.get('search', '')
    hotels = Hotel.objects.filter(name__icontains=search).values('id', 'name')[:10]
    return Response(list(hotels))


# Политика конфиденциальности
class PrivacyPolicyView(APIView):
    def get(self, request):
        lang = request.GET.get('lang', 'en')
        try:
            policy = PrivacyPolicy.objects.get(language_code=lang)
            return Response({'content': policy.content})
        except PrivacyPolicy.DoesNotExist:
            return Response({'content': ''})



class ContactThrottle(AnonRateThrottle):
    rate = '5/min'   # простая антиспам-защита

# @api_view(['POST'])
# @throttle_classes([ContactThrottle])
# def contact_questions(request):
#     data = request.data.copy()
#     data.setdefault('source', 'contacts')

#     # ✅ нормализуем текст вопроса из разных возможных полей
#     raw_q = data.get('question') or data.get('message') or data.get('text') or ''
#     data['question'] = str(raw_q).strip() or None

#     # защитимся от «левых» категорий
#     if data.get('category') not in dict(Question.CATEGORY_CHOICES):
#         data['category'] = 'other'

#     # 🔥 добавим обработку языка (иначе язык остаётся "None")
#     language = (data.get('language') or request.headers.get("Accept-Language") or "ru")[:5]
#     data['language'] = language

#     if settings.DEBUG:
#         print('[CONTACT_FORM] incoming:', dict(request.data))
#         print('[CONTACT_FORM] normalized:', data)

#     # ✅ передаём нормализованные данные, а не request.data
#     serializer = QuestionSerializer(data=data, context={'request': request})
#     if serializer.is_valid():
#         obj = serializer.save()
#         return Response({'ok': True, 'id': obj.id}, status=status.HTTP_201_CREATED)

#     return Response({'ok': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




