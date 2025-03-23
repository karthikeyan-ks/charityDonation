from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Organization, AdminNotification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                 'phone_number', 'address', 'profile_picture', 'is_organization',
                 'organization_name', 'organization_description', 'organization_website',
                 'organization_logo', 'user_type', 'registration_date')
        read_only_fields = ('id', 'registration_date')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name',
                 'phone_number', 'address', 'is_organization', 'organization_name',
                 'organization_description', 'organization_website', 'user_type')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class OrganizationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Organization
        fields = ('id', 'user', 'user_email', 'user_name', 'name', 'phone', 
                  'license_number', 'description', 'registration_certificate',
                  'approval_status', 'rejection_reason', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

class OrganizationRegistrationSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    # Organization fields
    name = serializers.CharField()
    phone = serializers.CharField()
    license_number = serializers.CharField()
    description = serializers.CharField()
    registration_certificate = serializers.FileField(required=False)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check if email is already registered
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already registered"})
            
        return attrs

class AdminNotificationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AdminNotification
        fields = ('id', 'notification_type', 'user', 'user_email', 'organization', 
                  'organization_name', 'message', 'is_read', 'created_at')
        read_only_fields = ('id', 'created_at') 