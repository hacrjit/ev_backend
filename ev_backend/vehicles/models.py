from django.db import models
from django.conf import settings

class Vehicle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    battery_capacity_kWh = models.FloatField(null=True, blank=True)
    registration_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.registration_number})"
