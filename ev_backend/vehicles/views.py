from rest_framework import viewsets, permissions
from .models import Vehicle
from .serializers import VehicleSerializer
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

class VehicleInfoView(APIView):
    def post(self, request):
        vehicle_no = request.data.get('vehicle_no')
        
        if not vehicle_no:
            return Response({"error": "Vehicle number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        url = "https://rto-vehicle-information-india.p.rapidapi.com/getVehicleInfo"
        payload = {
            "vehicle_no": vehicle_no,
            "consent": "Y",
            "consent_text": "I hereby give my consent for Eccentric Labs API to fetch my information"
        }
        headers = {
            "x-rapidapi-key": "797a172c6emshf6e34e33e19b312p1ed147jsn2343b32adabc",
            "x-rapidapi-host": "rto-vehicle-information-india.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            if data.get("status") == True:
                return Response(data.get("data"), status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to fetch vehicle info."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
