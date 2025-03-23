from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, DonationItemViewSet, 
                   DonationRequestViewSet, OrganizationNeedViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'items', DonationItemViewSet, basename='donation-item')
router.register(r'requests', DonationRequestViewSet, basename='donation-request')
router.register(r'needs', OrganizationNeedViewSet, basename='organization-need')

urlpatterns = [
    path('', include(router.urls)),
] 