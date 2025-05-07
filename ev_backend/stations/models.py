from django.contrib.gis.db import models

class ChargingStation(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField(geography=True)  # uses (longitude, latitude)
    address = models.TextField()
    available_ports = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return self.name