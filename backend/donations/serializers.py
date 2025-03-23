from rest_framework import serializers
from .models import Donation
from users.serializers import UserSerializer
from campaigns.serializers import CampaignSerializer

class DonationSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)
    campaign = CampaignSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = ('id', 'campaign', 'donor', 'amount', 'payment_status',
                 'payment_method', 'transaction_id', 'anonymous', 'message',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class DonationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ('campaign', 'amount', 'payment_method', 'anonymous', 'message') 