from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('DONOR', 'Donor'),
        ('ORGANIZATION', 'Organization'),
        ('ADMIN', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='DONOR')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    is_organization = models.BooleanField(default=False)
    organization_name = models.CharField(max_length=100, blank=True)
    organization_description = models.TextField(blank=True)
    organization_website = models.URLField(blank=True)
    organization_logo = models.ImageField(upload_to='organization_logos/', blank=True)
    is_test_user = models.BooleanField(default=False, help_text="Flag to identify test/dummy accounts")
    registration_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class Organization(models.Model):
    APPROVAL_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='organization_profile')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    description = models.TextField()
    registration_certificate = models.FileField(
        upload_to='organization_certificates/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        null=True,
        blank=True
    )
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_approved(self):
        return self.approval_status == 'APPROVED'

class AdminNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('NEW_DONOR', 'New Donor Registration'),
        ('NEW_ORGANIZATION', 'New Organization Registration'),
        ('ORGANIZATION_APPROVAL', 'Organization Approval Required'),
    )
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
