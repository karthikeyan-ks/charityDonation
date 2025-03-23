from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Donation
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
