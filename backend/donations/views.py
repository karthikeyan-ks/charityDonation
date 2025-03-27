from django.shortcuts import render,redirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Donation
from .form import DonationForm
from django.contrib.auth.decorators import login_required
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

from django.shortcuts import render, redirect
from .models import Donation

def donate_item(request):
    donations = Donation.objects.filter(donor=request.user)
    print(donations)

    if request.method == "POST":
        try:
            data = request.POST.dict()
            donor = request.user  # Assuming the user is authenticated
            print(data,donor)
            # Handle uploaded file (single image)
            uploaded_file = request.FILES.get('itemPhotos')  # Get only one file

            # Create a new Donation instance
            donation = Donation(
                donor=donor,
                item_category=data.get("itemCategory", "clothing"),
                other_category=data.get("otherCategory") or None,
                item_name=data.get("itemName", ""),
                item_description=data.get("itemDescription", ""),
                item_condition=data.get("itemCondition", "new"),
                item_quantity=int(data.get("itemQuantity", 1)),
                address_line1=data.get("addressLine1", ""),
                city=data.get("city", ""),
                state=data.get("state", ""),
                zip_code=data.get("zipCode", ""),
                pickup_availability=data.get("availability", "yes"),
                pickup_notes=data.get("pickupNotes", ""),
                additional_notes=data.get("additionalNotes", ""),
            )

            # Save the image if uploaded
            if uploaded_file:
                donation.uploaded_files = uploaded_file  # Assign image file
            print("Upload file :",uploaded_file)
            
            donation.save()  # Save the instance
            print(donation)

            donations = Donation.objects.filter(donor=request.user)

            return render(request, 'donor-dashboard.html', {"donations": donations, "success": "Donation added successfully!"})

        except Exception as e:
            print(e)
            return render(request, 'donor-dashboard.html', {"donations": donations, "error": str(e)})

    return render(request, 'donor-dashboard.html', {"donations": donations})





def donor_submit(request):
    return render(request, 'donsubmit.html')



def donor_delete(request,did): 
    if request.method == "POST":
        print(did)
        donation = Donation.objects.get(did=did)
        donation.delete()
    return redirect('donate_item')



def edit_donation(request, did):
    donation = Donation.objects.get(did=did)
    if request.method == "POST":
        form = DonationForm(request.POST, request.FILES, instance=donation)
        if form.is_valid():
            form.save()
            return redirect('donate_item')
    else:
        form = DonationForm(instance=donation)
    return render(request, 'edit_donation.html', {'form': form})

from django.contrib.auth import logout
def custom_logout(request):
    logout(request)
    return redirect('home')  # or wherever you want