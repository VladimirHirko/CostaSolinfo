from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from core.models import ExcursionPickupPoint


class Command(BaseCommand):
    help = "Удаляет записи EPP без отеля и склеивает дубли по (excursion, hotel)."

    def handle(self, *args, **options):
        with transaction.atomic():
            orph_qs = ExcursionPickupPoint.objects.filter(hotel__isnull=True)
            n_orph = orph_qs.count()
            orph_qs.delete()

            dups = (ExcursionPickupPoint.objects
                    .values('excursion_id', 'hotel_id')
                    .annotate(c=Count('id')).filter(c__gt=1))

            removed = 0
            for row in dups:
                items = list(ExcursionPickupPoint.objects
                             .filter(excursion_id=row['excursion_id'], hotel_id=row['hotel_id'])
                             .order_by('-pickup_time', '-id'))
                keep = items[0]
                for x in items[1:]:
                    updated = False
                    if not keep.pickup_time and x.pickup_time:
                        keep.pickup_time = x.pickup_time; updated = True
                    if keep.latitude is None and x.latitude is not None:
                        keep.latitude = x.latitude; updated = True
                    if keep.longitude is None and x.longitude is not None:
                        keep.longitude = x.longitude; updated = True
                    if not keep.pickup_point_name and x.pickup_point_name:
                        keep.pickup_point_name = x.pickup_point_name; updated = True
                    if updated:
                        keep.save()
                    x.delete()
                    removed += 1

        self.stdout.write(self.style.SUCCESS(
            f"Удалено без отеля: {n_orph}, удалено дублей: {removed}"
        ))
