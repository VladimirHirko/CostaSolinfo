# core/management/commands/audit_excursion_zones.py
from django.core.management.base import BaseCommand
from core.models import Hotel
import pandas as pd
import math

def _norm(s):
    if s is None:
        return ""
    return str(s).strip()

def _to_float(v):
    if v is None: return None
    try:
        s = str(v).strip().replace(",", ".")
        return float(s)
    except Exception:
        return None

def haversine_km(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError):
        return None
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon/2)**2)
    return 2 * R * math.asin(math.sqrt(a))

class Command(BaseCommand):
    help = (
        "Аудит временных зон у отелей: ищет отели, у которых ближайшая точка "
        "какой-то ДРУГОЙ зоны ближе, чем ближайшая точка назначенной зоны."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--excel",
            required=True,
            help="Путь к вашему excursions_template_compact.xlsx (лист 'pickup_points').",
        )
        parser.add_argument(
            "--delta",
            type=float,
            default=0.35,   # км: насколько ближе должна быть «чужая» зона, чтобы сработало предупреждение
            help="Порог (км), на сколько чужая зона должна быть ближе, чтобы пометить как сомнительное (default=0.35 км).",
        )
        parser.add_argument(
            "--far",
            type=float,
            default=2.0,    # км: слишком далеко от любых точек СВОЕЙ зоны
            help="Порог (км) для предупреждения 'слишком далеко от своей зоны' (default=2.0 км).",
        )
        parser.add_argument(
            "--csv",
            help="Если указать путь, выгрузит отчёт в CSV.",
        )

    def handle(self, *args, **opts):
        path = opts["excel"]
        delta_km = float(opts["delta"])
        far_km = float(opts["far"])
        out_csv = opts.get("csv")

        # 1) читаем точки
        try:
            df = pd.read_excel(path, sheet_name="pickup_points")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Не удалось прочитать {path}: {e}"))
            return

        for col in ("pickup_point_name", "zone", "direction"):
            if col not in df.columns:
                self.stderr.write(self.style.ERROR(
                    "Лист 'pickup_points' должен содержать столбцы: pickup_point_name, zone, direction, latitude, longitude"
                ))
                return

        df["pickup_point_name"] = df["pickup_point_name"].map(_norm)
        df["zone"] = df["zone"].map(_norm)
        df["direction"] = df["direction"].map(_norm)
        df["latitude"] = df.get("latitude", None).apply(_to_float)
        df["longitude"] = df.get("longitude", None).apply(_to_float)

        # карта: zone -> список точек (lat, lon, name)
        zone_points = {}
        for _, r in df.iterrows():
            z = _norm(r["zone"])
            name = _norm(r["pickup_point_name"])
            lat = r.get("latitude"); lon = r.get("longitude")
            if not z or not name or lat is None or lon is None:
                continue
            zone_points.setdefault(z, []).append((float(lat), float(lon), name))

        zones_total = len(zone_points)
        self.stdout.write(self.style.NOTICE(f"Найдено зон в Excel: {zones_total}"))

        # 2) проверяем отели
        rows = []
        warn_wrong = 0
        warn_far   = 0
        missing    = 0

        hotels = Hotel.objects.all().select_related("excursion_zone", "region")
        for h in hotels:
            z_assigned = getattr(h.excursion_zone, "name", None)
            if h.latitude is None or h.longitude is None or not z_assigned:
                missing += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned or "",
                    issue="NO_COORDS_OR_ZONE",
                    best_zone="", dist_assigned="", best_dist="",
                    note="Нет координат и/или не назначена временная зона"
                ))
                continue

            lat_h, lon_h = float(h.latitude), float(h.longitude)

            # ближайшая точка своей зоны
            dist_assigned = None
            if z_assigned in zone_points:
                for (lat, lon, _name) in zone_points[z_assigned]:
                    d = haversine_km(lat_h, lon_h, lat, lon)
                    if d is not None:
                        dist_assigned = d if dist_assigned is None else min(dist_assigned, d)

            # ближайшая точка среди всех зон
            best_zone = None
            best_dist = None
            best_name = None
            for z, plist in zone_points.items():
                for (lat, lon, pname) in plist:
                    d = haversine_km(lat_h, lon_h, lat, lon)
                    if d is None:
                        continue
                    if best_dist is None or d < best_dist:
                        best_dist = d
                        best_zone = z
                        best_name = pname

            # кейс 1: своей зоны нет в файле
            if dist_assigned is None:
                warn_wrong += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned,
                    issue="ASSIGNED_ZONE_HAS_NO_POINTS",
                    best_zone=best_zone or "", dist_assigned="",
                    best_dist=f"{best_dist:.3f}" if best_dist is not None else "",
                    note=f"В Excel нет точек для назначенной зоны; ближайшая зона: {best_zone} ({best_name})"
                ))
                continue

            # кейс 2: слишком далеко от своей зоны
            if dist_assigned > far_km:
                warn_far += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned,
                    issue="FAR_FROM_OWN_ZONE",
                    best_zone=best_zone or "", dist_assigned=f"{dist_assigned:.3f}",
                    best_dist=f"{best_dist:.3f}" if best_dist is not None else "",
                    note=f"До ближайшей точки своей зоны {dist_assigned:.2f} км (> {far_km} км)"
                ))

            # кейс 3: чужая зона заметно ближе своей
            if best_zone and best_dist + delta_km < dist_assigned:
                warn_wrong += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned,
                    issue="LIKELY_WRONG_ZONE",
                    best_zone=best_zone, dist_assigned=f"{dist_assigned:.3f}",
                    best_dist=f"{best_dist:.3f}",
                    note=f"Чужая зона '{best_zone}' ближе на ≥ {delta_km} км (ближайшая точка '{best_name}')"
                ))

        # вывод
        self.stdout.write(self.style.SUCCESS(
            f"Готово. Всего отелей: {hotels.count()}, пропуски: {missing}, "
            f"подозрительные: {warn_wrong}, далеко от своей зоны: {warn_far}."
        ))

        if rows:
            # короткий консольный обзор
            for r in rows[:20]:
                self.stdout.write(
                    f"[{r['issue']}] {r['hotel']}: assigned='{r['zone_assigned']}', "
                    f"best='{r['best_zone']}', dist_assigned='{r['dist_assigned']}', best_dist='{r['best_dist']}' "
                    f"| {r['note']}"
                )

        if out_csv:
            import csv
            with open(out_csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["hotel","zone_assigned","issue","best_zone","dist_assigned","best_dist","note"])
                w.writeheader()
                w.writerows(rows)
            self.stdout.write(self.style.NOTICE(f"Отчёт сохранён: {out_csv}"))
