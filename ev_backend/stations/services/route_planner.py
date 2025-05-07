from geopy.distance import geodesic
from django.contrib.gis.geos import Point
from stations.models import ChargingStation

def haversine_distance_km(p1, p2):
    return geodesic(p1, p2).km

def interpolate_points(p1, p2, step_km):
    dist = haversine_distance_km(p1, p2)
    num_points = int(dist // step_km)
    interpolated = []
    for i in range(1, num_points):
        lat = p1[0] + (p2[0] - p1[0]) * i / num_points
        lon = p1[1] + (p2[1] - p1[1]) * i / num_points
        interpolated.append((lat, lon))
    return interpolated

def build_full_route(route_points, max_direct_distance_km, step_km):
    full_route = [route_points[0]]
    for i in range(1, len(route_points)):
        p1 = (route_points[i - 1]['lat'], route_points[i - 1]['lon'])
        p2 = (route_points[i]['lat'], route_points[i]['lon'])
        dist = haversine_distance_km(p1, p2)
        if dist > max_direct_distance_km:
            full_route += interpolate_points(p1, p2, step_km)
        full_route.append(p2)
    return full_route

def find_nearby_stations(route_coords, radius_km):
    points = [Point(lon, lat) for lat, lon in route_coords]
    qs = ChargingStation.objects.all()
    nearby_stations = set()

    for point in points:
        qs_nearby = qs.filter(location__distance_lte=(point, radius_km * 1000))
        for station in qs_nearby:
            nearby_stations.add(station)

    return list(nearby_stations)
