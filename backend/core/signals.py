from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import activate, gettext as _
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import TransferNotification, TransferSchedule, TransferScheduleItem, TransferInquiry
#from .emails import send_transfer_change_email





# @receiver(pre_save, sender=TransferScheduleItem)
# def notify_time_change(sender, instance, **kwargs):
#     if not instance.pk:
#         return  # новый объект, не сравниваем

#     try:
#         old_instance = TransferScheduleItem.objects.get(pk=instance.pk)
#     except TransferScheduleItem.DoesNotExist:
#         return

#     if instance.time and old_instance.time != instance.time:
#         # ищем туриста по фамилии, дате и отелю
#         inquiries = TransferInquiry.objects.filter(
#             hotel=instance.hotel,
#             departure_date=instance.group.date,
#             last_name__iexact=instance.tourist_last_name,
#             replied=True
#         )

#         for inquiry in inquiries:
#             print(f"[INFO] Отправляем уведомление {inquiry.email} об изменении времени")  # временный лог

#             send_mail(
#                 subject="Изменение времени трансфера",
#                 message=(
#                     f"Уважаемый(ая) {inquiry.last_name},\n\n"
#                     f"Время вашего трансфера из отеля {instance.hotel.name} "
#                     f"на {instance.group.date.strftime('%d.%m.%Y')} было изменено.\n"
#                     f"Новое время выезда: {instance.time.strftime('%H:%M')}.\n\n"
#                     f"С уважением,\nКоманда CostaSolinfo"
#                 ),
#                 from_email="CostaSolinfo.Malaga@gmail.com",
#                 recipient_list=[inquiry.email],
#                 fail_silently=False
#             )

@receiver(pre_save, sender=TransferScheduleItem)
def notify_transfer_notification_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = TransferScheduleItem.objects.get(pk=instance.pk)
    except TransferScheduleItem.DoesNotExist:
        return

    if old_instance.time == instance.time:
        return  # Время не изменилось — ничего не делаем

    print(f"[DEBUG] Время трансфера изменилось для {instance.hotel.name} на {instance.time}")

    # Находим подписчиков на уведомление по отелю и дате
    notifications = TransferNotification.objects.filter(
        hotel=instance.hotel,
        departure_date=instance.group.date,
        transfer_type='group'
    )

    for notif in notifications:
        if notif.departure_time_sent == instance.time:
            print(f"[INFO] Уже отправлено время {instance.time} для {notif.email} — пропускаем")
            continue

        activate(notif.language)

        subject = _("Изменение времени трансфера")
        message = _(
            f"Уважаемый(ая),\n\n"
            f"Время вашего трансфера из отеля {instance.hotel.name} "
            f"на {notif.departure_date.strftime('%d.%m.%Y')} было изменено.\n"
            f"Новое время выезда: {instance.time.strftime('%H:%M')}.\n\n"
            f"С уважением,\nКоманда CostaSolinfo"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notif.email],
            fail_silently=False
        )

        print(f"[OK] Письмо отправлено на {notif.email}")

        # Обновляем отправленное время
        notif.departure_time_sent = instance.time
        notif.save(update_fields=["departure_time_sent"])
        print(f"[OK] Обновлено departure_time_sent для {notif.email}")


# @receiver(pre_save, sender=TransferSchedule)
# def notify_private_transfer_time_change(sender, instance, **kwargs):
#     if not instance.pk:
#         return  # Новый объект — не сравниваем

#     try:
#         old_instance = TransferSchedule.objects.get(pk=instance.pk)
#     except TransferSchedule.DoesNotExist:
#         return

#     # Проверяем: это индивидуальный трансфер и время изменилось
#     if instance.transfer_type != 'private' or old_instance.departure_time == instance.departure_time:
#         return

#     # Уведомления через TransferNotification
#     notifications = TransferNotification.objects.filter(
#         hotel=instance.hotel,
#         departure_date=instance.departure_date,
#         transfer_type='private'
#     )

#     for notif in notifications:
#         if notif.departure_time_sent == instance.departure_time:
#             continue  # Уже отправлено

#         activate(notif.language)

#         context = {
#             "hotel": instance.hotel.name,
#             "date": instance.departure_date.strftime('%d.%m.%Y'),
#             "time": instance.departure_time.strftime('%H:%M') if instance.departure_time else '',
#             "map_link": f"https://maps.google.com/?q={instance.pickup_point.latitude},{instance.pickup_point.longitude}" if instance.pickup_point else "#",
#         }

#         subject = "Transfer Information"
#         html_content = render_to_string("emails/transfer_notification_en.html", context)
#         text_content = strip_tags(html_content)

#         email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [notif.email])
#         email.attach_alternative(html_content, "text/html")
#         email.send()

#         notif.departure_time_sent = instance.departure_time
#         notif.save(update_fields=["departure_time_sent"])

#     # Уведомления по TransferInquiry
#     inquiries = TransferInquiry.objects.filter(
#         hotel=instance.hotel,
#         departure_date=instance.departure_date,
#         replied=True
#     )

#     for inquiry in inquiries:
#         subject = "Transfer Time Updated"
#         message = (
#             f"Dear {inquiry.last_name},\n\n"
#             f"The departure time of your transfer from the hotel {instance.hotel.name} "
#             f"on {instance.departure_date.strftime('%d.%m.%Y')} has been updated.\n"
#             f"New time: {instance.departure_time.strftime('%H:%M')}.\n\n"
#             f"Best regards,\nCostaSolinfo Team"
#         )

#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[inquiry.email],
#             fail_silently=False
#         )
