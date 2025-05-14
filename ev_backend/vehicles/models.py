from django.db import models
from django.conf import settings


class VehicleCatalog(models.Model):
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=100)
    battery_capacity_kWh = models.FloatField(null=True, blank=True)
    range_per_charge_km = models.FloatField(null=True, blank=True)
    charging_time = models.CharField(max_length=100, null=True, blank=True)
    connector_type = models.CharField(max_length=100, null=True, blank=True)
    charging_port_location = models.CharField(max_length=100, null=True, blank=True)
    fast_charging_support = models.BooleanField(default=False)
    dc_charging_compatibility = models.BooleanField(default=False)
    price_range = models.CharField(max_length=100, null=True, blank=True)
    launch_year = models.IntegerField(null=True, blank=True)
    availability = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model_name}"


class Vehicle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    catalog = models.ForeignKey(VehicleCatalog, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_vehicles')
    registration_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.catalog} ({self.registration_number})"