"""
Order serializers for checkout, orders, and subscriptions.
"""

from decimal import Decimal
from rest_framework import serializers
from django.conf import settings

from .models import Order, OrderItem, Subscription, SubscriptionItem
from apps.menu.serializers import MenuItemListSerializer
from apps.delivery.serializers import DeliveryWindowSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""

    menu_item_name = serializers.CharField(source='menu_item.name_en', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'menu_item_name', 'quantity',
            'unit_price', 'modifiers_snapshot', 'modifiers_total',
            'special_instructions', 'subtotal'
        ]
        read_only_fields = ['unit_price', 'modifiers_total', 'item_snapshot']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""

    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_window_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'subtotal', 'discount_amount', 'delivery_fee',
            'tax_rate', 'tax_amount', 'tax_type', 'total',
            'points_earned', 'points_redeemed', 'points_redemption_value',
            'delivery_date', 'delivery_window_display',
            'customer_notes', 'delivery_address_snapshot',
            'created_at', 'confirmed_at', 'delivered_at',
            'items'
        ]
        read_only_fields = [
            'order_number', 'subtotal', 'tax_amount', 'total',
            'points_earned', 'created_at', 'confirmed_at', 'delivered_at'
        ]

    def get_delivery_window_display(self, obj):
        if obj.delivery_window:
            return obj.delivery_window.display_time
        return None


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from checkout."""

    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    delivery_address_id = serializers.UUIDField(required=False)
    delivery_address = serializers.DictField(required=False)
    delivery_window_id = serializers.UUIDField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    points_to_redeem = serializers.IntegerField(required=False, default=0)
    customer_notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        # Must have either delivery_address_id or delivery_address
        if not attrs.get('delivery_address_id') and not attrs.get('delivery_address'):
            raise serializers.ValidationError({
                'delivery_address': 'Delivery address is required.'
            })
        return attrs

    def validate_items(self, value):
        """Validate cart items."""
        if not value:
            raise serializers.ValidationError('At least one item is required.')

        for item in value:
            if 'menu_item_id' not in item:
                raise serializers.ValidationError('Each item must have a menu_item_id.')
            if 'quantity' not in item or item['quantity'] < 1:
                raise serializers.ValidationError('Each item must have a valid quantity.')

        return value


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating Stripe payment intent."""

    items = serializers.ListField(child=serializers.DictField())
    delivery_address = serializers.DictField(required=False)
    delivery_window_id = serializers.UUIDField(required=False)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    points_to_redeem = serializers.IntegerField(required=False, default=0)


class ConfirmOrderSerializer(serializers.Serializer):
    """Serializer for confirming order after payment."""

    payment_intent_id = serializers.CharField()
    delivery_address_id = serializers.UUIDField(required=False)
    delivery_address = serializers.DictField(required=False)
    delivery_window_id = serializers.UUIDField()
    customer_notes = serializers.CharField(required=False, allow_blank=True)


class SubscriptionItemSerializer(serializers.ModelSerializer):
    """Serializer for subscription items."""

    menu_item_name = serializers.CharField(source='menu_item.name_en', read_only=True)

    class Meta:
        model = SubscriptionItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'week_number', 'modifiers']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""

    items = SubscriptionItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan_type', 'plan_type_display', 'billing_cycle',
            'status', 'status_display', 'next_billing_date', 'last_billing_date',
            'price_per_cycle', 'free_delivery', 'discount_percentage',
            'pause_until_date', 'skipped_weeks',
            'created_at', 'items'
        ]
        read_only_fields = [
            'stripe_subscription_id', 'stripe_customer_id',
            'created_at', 'updated_at'
        ]


class PauseSubscriptionSerializer(serializers.Serializer):
    """Serializer for pausing subscription."""

    pause_until_date = serializers.DateField()


class CancelSubscriptionSerializer(serializers.Serializer):
    """Serializer for cancelling subscription."""

    reason = serializers.CharField(required=False, allow_blank=True)


class SkipWeekSerializer(serializers.Serializer):
    """Serializer for skipping a delivery week."""

    week_date = serializers.DateField()
