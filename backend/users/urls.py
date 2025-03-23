from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('donors/login/', views.donor_login, name='donor-login'),
    path('donors/register/', views.donor_register, name='donor-register'),
    path('organizations/login/', views.organization_login, name='organization-login'),
    path('admin/login/', views.admin_login, name='admin-login'),
    
    # Registration endpoints
    path('organizations/register/', views.organization_register, name='organization-register'),
    
    # Admin organization management
    path('admin/organizations/pending/', views.admin_list_pending_organizations, name='admin-list-pending-organizations'),
    path('admin/organizations/approve/', views.admin_approve_organization, name='admin-approve-organization'),
    path('admin/organizations/', views.admin_list_organizations, name='admin-list-organizations'),
    path('admin/organizations/<int:org_id>/', views.admin_get_organization, name='admin-get-organization'),
    
    # Dashboard and notifications
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/notifications/', views.admin_notifications, name='admin-notifications'),
    path('admin/notifications/mark-read/', views.mark_notification_read, name='mark-all-notifications-read'),
    path('admin/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark-notification-read'),
] 