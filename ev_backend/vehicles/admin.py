from django.contrib import admin

# Register your models here.

from .models import VehicleCatalog, Vehicle
@admin.register(VehicleCatalog)
class VehicleCatalogAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model_name', 'vehicle_type', 'battery_capacity_kWh', 'range_per_charge_km', 'charging_time', 'connector_type', 'charging_port_location', 'fast_charging_support', 'dc_charging_compatibility', 'price_range', 'launch_year', 'availability')
    search_fields = ('brand', 'model_name')
    list_filter = ('vehicle_type', 'fast_charging_support', 'dc_charging_compatibility')
    ordering = ('brand', 'model_name')
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('user', 'catalog', 'registration_number')
    search_fields = ('registration_number',)
    list_filter = ('user', 'catalog')
    ordering = ('user', 'catalog')