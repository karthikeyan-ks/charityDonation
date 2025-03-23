from rest_framework import serializers
from .models import Campaign
from users.serializers import UserSerializer

class CampaignSerializer(serializers.ModelSerializer):
    organization = UserSerializer(read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'organization', 'target_amount',
                 'current_amount', 'start_date', 'end_date', 'status', 'image',
                 'created_at', 'updated_at', 'progress')
        read_only_fields = ('id', 'current_amount', 'created_at', 'updated_at')

    def get_progress(self, obj):
        return obj.progress_percentage()

class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ('title', 'description', 'target_amount', 'start_date', 'end_date', 'image') 