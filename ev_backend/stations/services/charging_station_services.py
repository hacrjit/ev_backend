from stations.models import ChargingStation
from django.contrib.gis.geos import Point, LineString
from django.db.models import Func


class ChargingStationService:
    @staticmethod
    def get_nearby_stations(user_location, radius):
        return ChargingStation.objects.filter(
            location__distance_lte=(user_location, D(km=radius))
        ).annotate(distance=Func('location', user_location, function='ST_Distance')).order_by('distance')

    @staticmethod
    def get_route_between_points(start_lat, start_lon, end_lat, end_lon, buffer_distance):
        start_point = Point(start_lon, start_lat, srid=4326)
        end_point = Point(end_lon, end_lat, srid=4326)
        route = LineString([start_point, end_point])
        route_buffer = route.buffer(buffer_distance)
        return ChargingStation.objects.filter(location__within=route_buffer)