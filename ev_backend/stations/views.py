import csv
import io
from rest_framework import viewsets, status
from .models import ChargingStation
from .serializers import ChargingStationSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from rest_framework.views import APIView
from django.contrib.gis.geos import LineString
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.gis.db.models.functions import Distance as GeoDistance

class ChargingStationViewSet(viewsets.ModelViewSet):
    queryset = ChargingStation.objects.all()
    serializer_class = ChargingStationSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = float(request.query_params.get('lat'))
        lon = float(request.query_params.get('lon'))
        radius_km = float(request.query_params.get('radius', 10))

        user_location = Point(lon, lat, srid=4326)
        nearby_stations = ChargingStation.objects.annotate(
            distance=Distance('location', user_location)
        ).filter(location__distance_lte=(user_location, D(km=radius_km))).order_by('distance')

        page = self.paginate_queryset(nearby_stations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(nearby_stations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        stations_data = request.data
        if not isinstance(stations_data, list):
            return Response({"error": "Expected a list of objects."}, status=status.HTTP_400_BAD_REQUEST)

        stations_to_create = []
        errors = []

        for index, entry in enumerate(stations_data):
            try:
                name = entry['name']
                address = entry['address']
                available_ports = int(entry['available_ports'])
                lat = float(entry['latitude'])
                lon = float(entry['longitude'])
                location = Point(lon, lat, srid=4326)

                station = ChargingStation(
                    name=name,
                    address=address,
                    available_ports=available_ports,
                    location=location
                )
                stations_to_create.append(station)

            except (KeyError, ValueError, TypeError) as e:
                errors.append({"index": index, "error": str(e)})

        if stations_to_create:
            ChargingStation.objects.bulk_create(stations_to_create, batch_size=1000)

        return Response({
            "message": f"{len(stations_to_create)} stations created successfully.",
            "errors": errors if errors else None
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)
    

    @action(detail=False, methods=['post'], url_path='upload-csv')
    def upload_csv(self, request):
        file = request.FILES.get('file')
        if not file or not file.name.endswith('.csv'):
            return Response({'error': 'A valid CSV file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        stations_to_create = []
        errors = []
        for idx, row in enumerate(reader):
            try:
                name = row['name']
                address = row['address']
                available_ports = int(row['available_ports'])
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                location = Point(lon, lat, srid=4326)

                station = ChargingStation(
                    name=name,
                    address=address,
                    available_ports=available_ports,
                    location=location
                )
                stations_to_create.append(station)
            except (KeyError, ValueError, TypeError) as e:
                errors.append({'row': idx + 1, 'error': str(e)})

        if stations_to_create:
            ChargingStation.objects.bulk_create(stations_to_create, batch_size=1000)

        return Response({
            'message': f'{len(stations_to_create)} stations uploaded successfully.',
            'errors': errors if errors else None
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)


























































































class NearbyChargingStations(APIView):
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request):
        lat = float(request.query_params.get('lat'))
        lng = float(request.query_params.get('lng'))
        radius = int(request.query_params.get('radius', 5000))
        
        user_location = Point(lng, lat, srid=4326)
        
        stations = ChargingStation.objects.filter(
            location__dwithin=(user_location, radius)
        ).annotate(
            distance=GeoDistance('location', user_location)
        ).order_by('distance')[:100]
        
        serializer = ChargingStationSerializer(stations, many=True)
        return Response(serializer.data)

class ViewportStations(APIView):
    def get(self, request):
        # Get bbox parameters (ne_lat, ne_lng, sw_lat, sw_lng)
        bbox = request.GET.get('bbox', '')
        try:
            ne_lat, ne_lng, sw_lat, sw_lng = map(float, bbox.split(','))
        except ValueError:
            return Response({'error': 'Invalid bbox format'}, status=400)

        # Create polygon from bbox coordinates
        bbox_polygon = Polygon.from_bbox((sw_lng, sw_lat, ne_lng, ne_lat))
        
        stations = ChargingStation.objects.filter(
            location__within=bbox_polygon
        )
        serializer = ChargingStationSerializer(stations, many=True)
        return Response(serializer.data)

class RouteStations(APIView):
    @method_decorator(cache_page(60 * 15))
    def post(self, request):
        route_coords = request.data.get('route', [])
        radius = int(request.data.get('radius', 10000))  # Default radius 10km

        if not route_coords:
            return Response({'error': 'No route provided'}, status=400)

        try:
            line_coords = [(point['lng'], point['lat']) for point in route_coords]
            route = LineString(line_coords, srid=4326)

            stations = ChargingStation.objects.filter(
                location__dwithin=(route, radius)
            )

            serializer = ChargingStationSerializer(stations, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({'error': str(e)}, status=400)