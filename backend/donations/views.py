from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Donation
import json
from .serializers import DonationSerializer, DonationCreateSerializer

# Create your views here.

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return DonationCreateSerializer
        return DonationSerializer

    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)

    @action(detail=False, methods=['get'])
    def my_donations(self, request):
        donations = self.get_queryset().filter(donor=request.user)
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

def donate_item(request):

    if request.method == "POST": 
        data = request.POST.dict()
        files = request.FILES.getlist('itemPhotos')  # Get multiple files if uploaded

        # Add file names to the data for reference
        data['uploaded_files'] = [file.name for file in files]

        # Convert to JSON (if needed for logging or processing)
        json_data = json.dumps(data, indent=4)

        # Print for debugging (remove in production)
        print(json_data)
    
    return render(request,'donor-dashboard.html')