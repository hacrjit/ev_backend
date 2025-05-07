# serializers.py
from rest_framework import serializers
from .models import ChargingStation
from django.contrib.gis.geos import Point

class ChargingStationSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    def get_longitude(self, obj):
        return obj.location.x  # POINT stores as (lng, lat)

    def get_latitude(self, obj):
        return obj.location.y

    class Meta:
        model = ChargingStation
        fields = ['id', 'name', 'address', 'available_ports', 'longitude', 'latitude']

    def create(self, validated_data):
        lat = validated_data.pop('latitude')
        lon = validated_data.pop('longitude')
        validated_data['location'] = Point(lon, lat)
        return super().create(validated_data)