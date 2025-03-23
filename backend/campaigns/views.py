from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Campaign
from .serializers import CampaignSerializer, CampaignCreateSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json

# Create your views here.

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CampaignCreateSerializer
        return CampaignSerializer

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user)

    @action(detail=True, methods=['get'])
    def donations(self, request, pk=None):
        campaign = self.get_object()
        donations = campaign.donations.all()
        from donations.serializers import DonationSerializer
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_campaigns(self, request):
        campaigns = self.get_queryset().filter(organization=request.user)
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data)

@csrf_exempt  # Use this for testing; remove in production for security
def admin_login(request):
    if request.method == 'POST':
        try:
            # Load JSON data from the request body
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Log the user in
                login(request, user)
                return JsonResponse({"success": True, "message": "Login successful"})
            else:
                return JsonResponse({"success": False, "message": "Invalid credentials"})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid request format"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})
