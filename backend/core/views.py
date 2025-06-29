import Levenshtein
from datetime import datetime
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view  # 🔧 Добавь это
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.http import JsonResponse
from core.models import (
    Homepage, InfoMeeting, AirportTransfer, Question, 
    ContactInfo, AboutUs, Excursion, TransferSchedule, Hotel,
    PageBanner, Hotel, PickupPoint, TransferNotification,
    TransferInquiry, TransferScheduleItem, TransferScheduleGroup
    )
from core.utils import send_html_email
from .serializers import (
    HomepageSerializer, InfoMeetingSerializer, AirportTransferSerializer,
    QuestionSerializer, ContactInfoSerializer, AboutUsSerializer, ExcursionSerializer,
    TransferScheduleRequestSerializer, TransferScheduleResponseSerializer,
    HotelSerializer, SimpleHotelSerializer, TransferNotificationCreateSerializer,
    TransferInquirySerializer
    )
from django.core.mail import send_mail
from django.contrib import admin
from django.urls import path
from django.utils.translation import activate, gettext as _
from django.shortcuts import render, redirect
from .forms import BulkTransferScheduleForm
from .models import Hotel, TransferSchedule

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

# Трансферы
class AirportTransferView(RetrieveAPIView):
    queryset = AirportTransfer.objects.all()
    serializer_class = AirportTransferSerializer

    def get_object(self):
        return self.queryset.first()

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
                    time = form.cleaned_data.get(time_field)
                    point = form.cleaned_data.get(point_field)

                    if time and point:
                        TransferSchedule.objects.create(
                            transfer_type=transfer_type,
                            date=transfer_date,
                            hotel=hotel,
                            pickup_point=point,
                            departure_time=time
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
        transfers = TransferSchedule.objects.filter(
            hotel_id=hotel_id,
            departure_date=date,
            transfer_type=transfer_type
        ).order_by('departure_time')

        if not transfers.exists():
            return Response({'error': 'No transfer schedule found'}, status=404)

        if transfer_type == 'private':
            from Levenshtein import distance as levenshtein_distance

            # 🔍 Если указана фамилия — ищем совпадение
            if last_name:
                match = transfers.filter(passenger_last_name__iexact=last_name).first()
                if match:
                    pickup_point = PickupPoint.objects.filter(hotel=match.hotel, transfer_type=transfer_type).first()
                    return Response({
                        "success": True,
                        "pickup_time": match.departure_time.strftime("%H:%M"),
                        "pickup_point": pickup_point.name if pickup_point else "—",
                        "pickup_lat": pickup_point.latitude if pickup_point else None,
                        "pickup_lng": pickup_point.longitude if pickup_point else None,
                    })

                # ❌ Не найдено — ищем похожие фамилии
                candidates = []
                for ln in transfers.values_list('passenger_last_name', flat=True):
                    if ln:
                        dist = levenshtein_distance(last_name.lower(), ln.lower())
                        if 0 < dist <= 3:
                            candidates.append((dist, ln))

                if candidates:
                    candidates.sort()
                    best_guess = candidates[0][1]
                    return Response({
                        "success": False,
                        "reason": "no_exact_match",
                        "suggestion": best_guess
                    }, status=200)

                return Response({
                    "success": False,
                    "reason": "not_found",
                    "message": "Фамилия не найдена. Проверьте правильность написания."
                }, status=200)

            # ⛔ Фамилия не указана, но несколько трансферов
            if transfers.count() > 1:
                return Response({
                    "success": False,
                    "reason": "multiple_transfers",
                    "message": "На данную дату из этого отеля выезжает несколько семей. Уточните фамилию."
                }, status=200)

            # ✅ Только один трансфер — можно отдать сразу
            transfer = transfers.first()
            pickup_point = PickupPoint.objects.filter(hotel=transfer.hotel, transfer_type=transfer_type).first()
            return Response({
                "success": True,
                "pickup_time": transfer.departure_time.strftime("%H:%M"),
                "pickup_point": pickup_point.name if pickup_point else "—",
                "pickup_lat": pickup_point.latitude if pickup_point else None,
                "pickup_lng": pickup_point.longitude if pickup_point else None,
            })


        else:
            # Групповой трансфер
            transfer = transfers.first()
            pickup_point = PickupPoint.objects.filter(hotel=transfer.hotel, transfer_type=transfer_type).first()
            return Response({
                "pickup_time": transfer.departure_time.strftime("%H:%M"),
                "pickup_point": pickup_point.name if pickup_point else "—",
                "pickup_lat": pickup_point.latitude if pickup_point else None,
                "pickup_lng": pickup_point.longitude if pickup_point else None,
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


# Вьюха отправки писем подписчикам по трансферам
class TransferNotificationViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TransferNotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            # Получаем трансфер (TransferScheduleItem внутри группы)
            group = TransferScheduleGroup.objects.filter(
                date=instance.departure_date,
                transfer_type__iexact=instance.transfer_type
            ).first()

            transfer_item = TransferSchedule.objects.filter(
                group=group,
                hotel=instance.hotel
            ).first()


            # Время трансфера (из поля time, не departure_time!)
            departure_time = transfer_item.departure_time if transfer_item else None
            departure_time_str = departure_time.strftime('%H:%M') if departure_time else _("—")

            # Пробуем получить точку сбора
            pickup_point = None
            if transfer_item and transfer_item.pickup_point:
                pickup_point = transfer_item.pickup_point
            else:
                from core.models import PickupPoint
                pickup_point = PickupPoint.objects.filter(
                    hotel=instance.hotel,
                    transfer_type=instance.transfer_type
                ).first()

            # Название и карта
            pickup_name = pickup_point.name if pickup_point else _("не указана")
            map_link = (
                f"https://www.google.com/maps?q={pickup_point.latitude},{pickup_point.longitude}"
                if pickup_point and pickup_point.latitude and pickup_point.longitude
                else None
            )

            # Устанавливаем язык
            activate(instance.language)

            # Отправляем HTML-письмо
            send_html_email(
                subject = "Airport transfer details",
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

            # Сохраняем время отправки
            if departure_time:
                instance.departure_time_sent = departure_time
                instance.save(update_fields=["departure_time_sent"])

            return Response({"detail": _("Информация отправлена на почту.")}, status=201)

        return Response(serializer.errors, status=400)

        
# Вьюшка обратной связи по индивидуальтным трансферам
class TransferInquiryViewSet(viewsets.ModelViewSet):
    queryset = TransferInquiry.objects.all()
    serializer_class = TransferInquirySerializer
    http_method_names = ['post']  # только POST для внешнего доступа

    def perform_create(self, serializer):
        inquiry = serializer.save()
        # Отправка подтверждения туристу
        send_mail(
            subject="Ваш запрос принят",
            message=(
                f"Уважаемый(ая) {inquiry.last_name},\n\n"
                f"Мы получили ваш запрос по трансферу.\n"
                f"Дата: {inquiry.departure_date}\n"
                f"Отель: {inquiry.hotel.name if inquiry.hotel else '—'}\n"
                f"Номер рейса: {inquiry.flight_number or '—'}\n\n"
                f"Мы свяжемся с вами в ближайшее время."
            ),
            from_email="info@costasolinfo.com",
            recipient_list=[inquiry.email],
        )


class QuestionView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_object(self):
        return self.queryset.first()

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

class ExcursionView(RetrieveAPIView):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionSerializer

    def get_object(self):
        return self.queryset.first()  # если только одна экскурсия, иначе делаем ListAPIView

# Поисковая система по отелям
@api_view(['GET'])
def hotel_search(request):
    search = request.GET.get('search', '')
    hotels = Hotel.objects.filter(name__icontains=search).values('id', 'name')[:10]
    return Response(list(hotels))