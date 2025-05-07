from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from stations.models import ChargingStation  # Replace with your app name

class Command(BaseCommand):
    help = 'Backfill location PointField from latitude and longitude fields'

    def handle(self, *args, **kwargs):
        updated = 0
        for station in ChargingStation.objects.all():
            if station.latitude and station.longitude:
                point = Point(station.longitude, station.latitude)  # longitude, latitude
                if station.location != point:
                    station.location = point
                    station.save()
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} stations with location field."))
