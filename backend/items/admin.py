from django.contrib import admin
from .models import Category, DonationItem, DonationRequest, OrganizationNeed

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')

@admin.register(DonationItem)
class DonationItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'donor', 'category', 'condition', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'condition', 'category', 'created_at')
    search_fields = ('name', 'description', 'donor__email', 'donor__first_name', 'donor__last_name')
    raw_id_fields = ('donor', 'category')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'organization', 'status', 'pickup_date', 'pickup_time', 'created_at')
    list_filter = ('status', 'pickup_date', 'created_at')
    search_fields = ('item__name', 'organization__email', 'organization__organization_name', 'message')
    raw_id_fields = ('organization', 'item')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(OrganizationNeed)
class OrganizationNeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'category', 'quantity_needed', 'status', 'deadline')
    list_filter = ('status', 'category', 'deadline', 'created_at')
    search_fields = ('name', 'description', 'organization__email', 'organization__organization_name')
    raw_id_fields = ('organization', 'category')
    readonly_fields = ('created_at', 'updated_at')
