from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import activate, gettext as _
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import TransferNotification, TransferSchedule

@receiver(post_save, sender=TransferNotification)
def send_transfer_email_notification(sender, instance, created, **kwargs):
    if not created:
        return

    activate(instance.language)

    try:
        schedule = TransferSchedule.objects.get(
            hotel=instance.hotel,
            departure_date=instance.departure_date,
            transfer_type=instance.transfer_type,
        )
    except TransferSchedule.DoesNotExist:
        return

    pickup_point = schedule.pickup_point
    pickup_point_name = pickup_point.name if pickup_point else _("не указана")
    coords = f"{pickup_point.latitude}, {pickup_point.longitude}" if pickup_point else _("не указано")
    maps_link = f"https://www.google.com/maps?q={pickup_point.latitude},{pickup_point.longitude}" if pickup_point else None

    context = {
        "departure_time": schedule.departure_time,
        "pickup_point_name": pickup_point_name,
        "coords": coords,
        "maps_link": maps_link,
    }

    subject = _("Информация о вашем трансфере")
    html_content = render_to_string("emails/transfer_notification.html", context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [instance.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
