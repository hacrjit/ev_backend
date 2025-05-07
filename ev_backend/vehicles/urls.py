from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, VehicleInfoView

router = DefaultRouter()
router.register(r'', VehicleViewSet, basename='vehicles')

urlpatterns = [
    path('vehicle-info/', VehicleInfoView.as_view(), name='vehicle-info'),
    path('', include(router.urls)),
]
