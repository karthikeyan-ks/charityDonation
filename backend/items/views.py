from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, DonationItem, DonationRequest, OrganizationNeed
from .serializers import (CategorySerializer, DonationItemSerializer,
                        DonationRequestSerializer, OrganizationNeedSerializer)

# Create your views here.

class IsOrganizationUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_organization

class IsDonorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_organization

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Allow public access to categories

class DonationItemViewSet(viewsets.ModelViewSet):
    serializer_class = DonationItemSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsDonorUser]  # Only donors can create donations
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return DonationItem.objects.filter(status='available')
        if self.request.user.is_organization:
            return DonationItem.objects.filter(status='available')
        return DonationItem.objects.filter(donor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        item = self.get_object()
        if item.donor != request.user:
            return Response(
                {'error': 'Not authorized to cancel this donation'},
                status=status.HTTP_403_FORBIDDEN
            )
        item.status = 'cancelled'
        item.save()
        return Response({'status': 'donation cancelled'})

class DonationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = DonationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_organization:
            return DonationRequest.objects.filter(organization=self.request.user)
        return DonationRequest.objects.filter(item__donor=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        donation_request = self.get_object()
        if donation_request.item.donor != request.user:
            return Response(
                {'error': 'Not authorized to approve this request'},
                status=status.HTTP_403_FORBIDDEN
            )
        donation_request.status = 'approved'
        donation_request.item.status = 'pending'
        donation_request.save()
        donation_request.item.save()
        return Response({'status': 'request approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        donation_request = self.get_object()
        if donation_request.item.donor != request.user:
            return Response(
                {'error': 'Not authorized to reject this request'},
                status=status.HTTP_403_FORBIDDEN
            )
        donation_request.status = 'rejected'
        donation_request.save()
        return Response({'status': 'request rejected'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        donation_request = self.get_object()
        if donation_request.organization != request.user:
            return Response(
                {'error': 'Not authorized to complete this request'},
                status=status.HTTP_403_FORBIDDEN
            )
        donation_request.status = 'completed'
        donation_request.item.status = 'donated'
        donation_request.save()
        donation_request.item.save()
        return Response({'status': 'donation completed'})

class OrganizationNeedViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationNeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_organization:
            return OrganizationNeed.objects.filter(organization=self.request.user)
        return OrganizationNeed.objects.filter(status='active')
