from django.shortcuts import render,redirect
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
    donations = Donation.objects.filter(donor = request.user)
    if request.method == "POST":
        try:
            # Extract data from request
            data = request.POST.dict()
            donor = request.user  # Assuming the user is authenticated
            
            # Handle uploaded files
            files = request.FILES.getlist('itemPhotos')
            file_names = [file.name for file in files]

            # Create a DonationItem instance
            donation = Donation.objects.create(
                donor=donor,
                item_category=data.get("itemCategory", ""),
                other_category=data.get("otherCategory", "") or None,
                item_name=data.get("itemName", ""),
                item_description=data.get("itemDescription", ""),
                item_condition=data.get("itemCondition", ""),
                item_quantity=int(data.get("itemQuantity", 1)),
                address_line1=data.get("addressLine1", ""),
                city=data.get("city", ""),
                state=data.get("state", ""),
                zip_code=data.get("zipCode", ""),
                pickup_availability=data.get("availability", ""),  # Store as CSV string
                pickup_notes=data.get("pickupNotes", ""),
                additional_notes=data.get("additionalNotes", ""),
                uploaded_files=file_names,  # Save file names in JSON field
            )

            donations = Donation.objects.filter(donor = request.user)

            return render(request, 'donor-dashboard.html',{"donations":donations})

        except Exception as e:
            return render(request, 'donor-dashboard.html',{"donations":donations})

    return render(request, 'donor-dashboard.html',{"donations":donations})

def donor_submit(request):

    return render(request, 'donsubmit.html')