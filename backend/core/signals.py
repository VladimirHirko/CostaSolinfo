from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import activate, gettext as _
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import (
    TransferNotification, TransferSchedule, TransferScheduleItem, 
    TransferInquiry, TransferScheduleGroup, Hotel
)
#from .emails import send_transfer_change_email





@receiver(post_save, sender=TransferScheduleGroup)
def notify_transfer_group_updated(sender, instance, **kwargs):
    transfer_type = instance.transfer_type
    group_date = instance.date

    print("===============================================")
    print(f"[DEBUG] Группа трансфера сохранена: {group_date} ({transfer_type})")
    print("===============================================")

    # Получаем все связанные TransferScheduleItem
    items = TransferScheduleItem.objects.filter(group=instance)

    for item in items:
        hotel = item.hotel
        new_time = item.time
        last_name = (item.tourist_last_name or "").strip().lower()

        print(f"\n[ITEM] Отель: {hotel}, Время: {new_time}, Фамилия: {last_name}")

        if transfer_type == 'group':
            print("[INFO] Это групповой трансфер.")
            notifications = TransferNotification.objects.filter(
                hotel=hotel,
                departure_date=group_date,
                transfer_type='group'
            )
            print(f"[DEBUG] Найдено групповых подписчиков: {notifications.count()}")

        elif transfer_type == 'private':
            print("[INFO] Это индивидуальный трансфер.")

            if not last_name:
                print("[WARN] Не указана фамилия туриста — пропускаем.")
                continue

            all_notifications = TransferNotification.objects.filter(
                hotel=hotel,
                departure_date=group_date,
                transfer_type='private'
            )

            print(f"[DEBUG] Целевая фамилия для сравнения: '{last_name}'")
            print(f"[DEBUG] Всего найдено подписчиков: {all_notifications.count()}")

            notifications = []
            for notif in all_notifications:
                notif_lastname = (notif.last_name or "").strip().lower()
                print(f"[CHECK] Сравнение: '{notif_lastname}' == '{last_name}'")

                if notif_lastname == last_name:
                    print(f"[MATCH] Совпадение найдено: {notif.email}")
                    notifications.append(notif)

            print(f"[RESULT] Найдено совпадений по фамилии: {len(notifications)}")

        else:
            print("[WARN] Неизвестный тип трансфера — пропускаем item.")
            continue

        # Отправка писем
        for notif in notifications:
            if notif.departure_time_sent == new_time:
                print(f"[INFO] Уже отправлено время {new_time} для {notif.email} — пропускаем")
                continue

            activate(notif.language)

            subject = _("Изменение времени трансфера")
            message = _(
                f"Уважаемый(ая),\n\n"
                f"Время вашего трансфера из отеля {hotel.name} "
                f"на {group_date.strftime('%d.%m.%Y')} было изменено.\n"
                f"Новое время выезда: {new_time.strftime('%H:%M')}.\n\n"
                f"С уважением,\nКоманда CostaSolinfo"
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notif.email],
                    fail_silently=False
                )
                print(f"[OK] Письмо отправлено на {notif.email}")
            except Exception as e:
                print(f"[ERROR] Ошибка при отправке письма {notif.email}: {e}")
                continue

            notif.departure_time_sent = new_time
            notif.save(update_fields=["departure_time_sent"])
            print(f"[OK] Обновлено departure_time_sent для {notif.email}")



def autowire_hotel_excursions(sender, instance, created, **kwargs):
    """
    После сохранения отеля: если выставлена excursion_zone,
    создаём/обновляем строки ExcursionPickupPoint для всех Excursion,
    беря эталонное время/точку из первого найденного отеля той же зоны.
    Если в зоне ещё нет расписания – просто выходим (оно подтянется после импорта).
    """
    # если нет временной зоны — ничего не делаем
    if not getattr(instance, "excursion_zone_id", None):
        return

    # ЛЕНИВО получаем модели, чтобы не ловить NameError
    Excursion = apps.get_model("core", "Excursion")
    ExcursionPickupPoint = apps.get_model("core", "ExcursionPickupPoint")
    # Hotel = apps.get_model("core", "Hotel")  # не требуется прямо здесь

    with transaction.atomic():
        for exc in Excursion.objects.all().only("id"):
            # Эталон по зоне: любая запись этой экскурсии у отеля с той же зоной
            sample = (
                ExcursionPickupPoint.objects
                .filter(excursion=exc, hotel__excursion_zone_id=instance.excursion_zone_id)
                .values("pickup_time", "pickup_point_name", "latitude", "longitude")
                .first()
            )
            if not sample:
                # в зоне пока нет времени/точки — подтянется после импорта Excel
                continue

            # Точка отеля имеет приоритет, если задана
            pp_name = sample["pickup_point_name"]
            lat = sample["latitude"]
            lng = sample["longitude"]

            hotel_pp = getattr(instance, "pickup_point", None)
            if getattr(hotel_pp, "name", None):
                pp_name = hotel_pp.name
                lat = getattr(hotel_pp, "latitude", lat)
                lng = getattr(hotel_pp, "longitude", lng)

            obj, created_epp = ExcursionPickupPoint.objects.get_or_create(
                excursion=exc,
                hotel=instance,
                defaults={
                    "pickup_time": sample["pickup_time"],
                    "pickup_point_name": pp_name,
                    "latitude": lat,
                    "longitude": lng,
                },
            )

            if not created_epp:
                updates = {}
                if obj.pickup_time != sample["pickup_time"]:
                    updates["pickup_time"] = sample["pickup_time"]
                if obj.pickup_point_name != pp_name and pp_name:
                    updates["pickup_point_name"] = pp_name
                if lat is not None and obj.latitude != lat:
                    updates["latitude"] = lat
                if lng is not None and obj.longitude != lng:
                    updates["longitude"] = lng

                if updates:
                    for k, v in updates.items():
                        setattr(obj, k, v)
                    obj.save(update_fields=list(updates.keys()))


def connect_signals():
    """
    Подключаем сигнал лениво, чтобы не импортировать модели в модуле.
    """
    Hotel = apps.get_model("core", "Hotel")
    post_save.connect(
        autowire_hotel_excursions,
        sender=Hotel,
        dispatch_uid="core.autowire_hotel_excursions",
    )