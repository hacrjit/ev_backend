from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChargingStationViewSet, RouteStations, NearbyChargingStations, ViewportStations

router = DefaultRouter()
router.register('', ChargingStationViewSet)

urlpatterns = [
    path('route/', RouteStations.as_view(), name='route_stations'),
    path('nearby/', NearbyChargingStations.as_view(), name='nearby_stations'),
    path('viewport/', ViewportStations.as_view(), name='viewport_stations'),
    # path('', include(router.urls))
]