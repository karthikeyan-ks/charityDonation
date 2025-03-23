"""
URL configuration for charity_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import (
    UserViewSet, donor_login, organization_login, organization_register,
    admin_approve_organization, admin_list_organizations, admin_get_organization,
    admin_login, admin_dashboard, approve_organization, check_organization_status,
    admin_list_donors, admin_get_donor
)
from django.views.generic import RedirectView, TemplateView
from django.http import FileResponse
import os
from django.views.static import serve
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json

router = DefaultRouter()
router.register(r'users', UserViewSet)

def serve_html(request, filename):
    try:
        # Remove .html extension if present
        if filename.endswith('.html'):
            filename = filename[:-5]
        
        # Add .html extension back for file lookup
        file_path = os.path.join(settings.BASE_DIR.parent, 'frontend', f"{filename}.html")
        
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create response with proper content type
        response = HttpResponse(content, content_type='text/html')
        return response
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)

urlpatterns = [
   
    path('api/', include(router.urls)),
    path('api/items/', include('items.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('rest_framework.urls')),
    
    # Authentication endpoints
    path('api/admin/login/', admin_login, name='api_admin_login'),
    path('api/admin/dashboard/', admin_dashboard, name='api_admin_dashboard'),
    path('api/donor/login/', donor_login, name='donor_login'),
    path('api/organization/login/', organization_login, name='organization_login'),
    path('api/organization/register/', organization_register, name='organization_register'),
    path('api/organization/status/<int:org_id>/', check_organization_status, name='check_organization_status'),
    path('api/admin/organizations/', admin_list_organizations, name='admin_list_organizations'),
    path('api/admin/organizations/<int:org_id>/', admin_get_organization, name='admin_get_organization'),
    path('api/admin/organizations/approve/', admin_approve_organization, name='admin_approve_organization'),
    path('api/admin/organizations/<int:org_id>/<str:action>/', approve_organization, name='approve_organization'),
    path('api/admin/donors/', admin_list_donors, name='admin_list_donors'),
    path('api/admin/donors/<int:donor_id>/', admin_get_donor, name='admin_get_donor'),
    
    # Frontend routes
    path('', serve_html, {'filename': 'index'}),
    path('login/', serve_html, {'filename': 'login'}),
    path('about/', serve_html, {'filename': 'about'}),
    path('contact/', serve_html, {'filename': 'contact'}),
    path('admin-dashboard/', serve_html, {'filename': 'admin-dashboard'}),
    path('admin-donors/', serve_html, {'filename': 'admin-donors'}),
    path('admin-organizations/', serve_html, {'filename': 'admin-organizations'}),
    path('admin-login/', serve_html, {'filename': 'admin-login-page'}),
    path('donor/', serve_html, {'filename': 'donor'}),
    path('org/', serve_html, {'filename': 'org'}),
    path('orgsubmit/', serve_html, {'filename': 'orgsubmit'}),
    path('donsubmit/', serve_html, {'filename': 'donsubmit'}),
    path('forget/', serve_html, {'filename': 'forget'}),
    path('reset-password/', serve_html, {'filename': 'reset-password'}),
    path('org-pending/', serve_html, {'filename': 'org-pending'}),
    
    # Handle direct .html requests
    path('<str:filename>.html', serve_html, name='html_page'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve files from frontend directory
    urlpatterns += [
        path('static/css/<path:path>', serve, {'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend/css')}),
        path('static/js/<path:path>', serve, {'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend/js')}),
        path('static/images/<path:path>', serve, {'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend/images')}),
        path('static/fonts/<path:path>', serve, {'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend/fonts')}),
        # Add direct image serving
        path('images/<path:path>', serve, {'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend/images')}),
    ]

@csrf_exempt  # Use this for testing; remove in production
def admin_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"success": True, "message": "Login successful"})
            else:
                return JsonResponse({"success": False, "message": "Invalid username or password. Please try again."})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid request format"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})
