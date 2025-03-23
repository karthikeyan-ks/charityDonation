from django.contrib import admin
from django.db.models import Q
from .models import CustomUser, Organization

def mark_as_test_users(modeladmin, request, queryset):
    queryset.update(is_test_user=True)
mark_as_test_users.short_description = "Mark selected users as test users"

def delete_test_users(modeladmin, request, queryset):
    # Find users with test-related keywords in their details
    dummy_patterns = ['test', 'dummy', 'example', 'demo', 'fake', 'sample']
    dummy_q = Q()
    for pattern in dummy_patterns:
        dummy_q |= (
            Q(username__icontains=pattern) | 
            Q(email__icontains=pattern) | 
            Q(first_name__icontains=pattern) | 
            Q(last_name__icontains=pattern)
        )
    
    # Filter non-admin users that match the patterns
    dummy_users = CustomUser.objects.filter(dummy_q).exclude(user_type='ADMIN')
    
    # Delete the users
    count = dummy_users.count()
    dummy_users.delete()
    
    modeladmin.message_user(request, f"Successfully deleted {count} dummy users")
delete_test_users.short_description = "Delete all dummy/test users"

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_organization')
    list_filter = ('user_type', 'is_organization')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = [mark_as_test_users, delete_test_users]

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'approval_status', 'created_at')
    list_filter = ('approval_status',)
    search_fields = ('name', 'user__username', 'user__email')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
