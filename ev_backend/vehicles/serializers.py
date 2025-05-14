from rest_framework import serializers
from .models import Vehicle, VehicleCatalog

class VehicleCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCatalog
        fields = '__all__'
        read_only_fields = ['user']

class VehicleSerializer(serializers.ModelSerializer):
    catalog = VehicleCatalogSerializer(read_only=True)
    catalog_id = serializers.PrimaryKeyRelatedField(
        queryset=VehicleCatalog.objects.all(),
        source='catalog',
        write_only=True
    )

    class Meta:
        model = Vehicle
        fields = ['id', 'user', 'catalog', 'catalog_id', 'registration_number']
        read_only_fields = ['user']
