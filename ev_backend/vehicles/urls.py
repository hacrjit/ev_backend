from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, VehicleCatalogViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'catalog', VehicleCatalogViewSet, basename='catalog')

urlpatterns = [
    # path('vehicle-info/', VehicleInfoView.as_view(), name='vehicle-info'),
    path('', include(router.urls)),
]
