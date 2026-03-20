"""
Delivery API Serializers.
"""

from rest_framework import serializers
from .models import DeliveryZone, DeliveryWindow


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = [
            'id', 'postal_code_prefix', 'label', 'city',
            'delivery_fee', 'free_delivery_threshold', 'is_active'
        ]


class DeliveryWindowSerializer(serializers.ModelSerializer):
    display_time = serializers.CharField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    spots_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeliveryWindow
        fields = [
            'id', 'date', 'time_start', 'time_end', 'display_time',
            'is_available', 'spots_remaining', 'cutoff_datetime'
        ]
