from rest_framework import serializers
from .models import Category, DonationItem, DonationRequest, OrganizationNeed
from users.models import CustomUser

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class DonationItemSerializer(serializers.ModelSerializer):
    donor_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = DonationItem
        fields = ['id', 'donor', 'donor_name', 'category', 'category_name', 'name', 
                 'description', 'condition', 'quantity', 'status', 'image', 
                 'pickup_address', 'created_at', 'updated_at']
        read_only_fields = ['donor', 'status']

    def get_donor_name(self, obj):
        return obj.donor.get_full_name() or obj.donor.username

    def get_category_name(self, obj):
        return obj.category.name

    def create(self, validated_data):
        validated_data['donor'] = self.context['request'].user
        return super().create(validated_data)

class DonationRequestSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()

    class Meta:
        model = DonationRequest
        fields = ['id', 'organization', 'organization_name', 'item', 'item_name',
                 'status', 'message', 'pickup_date', 'pickup_time', 'created_at', 
                 'updated_at']
        read_only_fields = ['organization', 'status']

    def get_organization_name(self, obj):
        return obj.organization.organization_name

    def get_item_name(self, obj):
        return obj.item.name

    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user
        return super().create(validated_data)

class OrganizationNeedSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationNeed
        fields = ['id', 'organization', 'organization_name', 'category', 
                 'category_name', 'name', 'description', 'quantity_needed',
                 'status', 'deadline', 'created_at', 'updated_at']
        read_only_fields = ['organization']

    def get_organization_name(self, obj):
        return obj.organization.organization_name

    def get_category_name(self, obj):
        return obj.category.name

    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user
        return super().create(validated_data) 