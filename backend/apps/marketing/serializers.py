"""
Marketing serializers for coupons, loyalty, and referrals.
"""

from rest_framework import serializers
from .models import Coupon, LoyaltyPoint, ReferralHistory, POINTS_TO_DOLLAR_RATE


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons."""

    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'min_order_amount', 'max_discount_amount',
            'is_first_order_only', 'is_subscription_only',
            'expiry_date', 'is_valid'
        ]


class ValidateCouponSerializer(serializers.Serializer):
    """Serializer for coupon validation request."""

    code = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class ValidateCouponResponseSerializer(serializers.Serializer):
    """Serializer for coupon validation response."""

    valid = serializers.BooleanField()
    coupon = CouponSerializer(required=False)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    message = serializers.CharField()


class LoyaltyPointSerializer(serializers.ModelSerializer):
    """Serializer for loyalty point transactions."""

    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = LoyaltyPoint
        fields = [
            'id', 'points_delta', 'balance_after', 'reason', 'reason_display',
            'description', 'order', 'created_at'
        ]


class LoyaltyBalanceSerializer(serializers.Serializer):
    """Serializer for loyalty balance response."""

    balance = serializers.IntegerField()
    dollar_value = serializers.SerializerMethodField()
    recent_transactions = LoyaltyPointSerializer(many=True)

    def get_dollar_value(self, obj):
        return f"{obj['balance'] / POINTS_TO_DOLLAR_RATE:.2f}"


class RedeemPointsSerializer(serializers.Serializer):
    """Serializer for redeeming points."""

    points = serializers.IntegerField(min_value=1)

    def validate_points(self, value):
        """Ensure user has enough points."""
        user = self.context['request'].user
        if hasattr(user, 'profile') and value > user.profile.wela_points_balance:
            raise serializers.ValidationError(
                f"Insufficient points. You have {user.profile.wela_points_balance} points."
            )
        return value


class ReferralHistorySerializer(serializers.ModelSerializer):
    """Serializer for referral history."""

    referrer_email = serializers.CharField(source='referrer.email', read_only=True)
    referred_email = serializers.CharField(source='referred_user.email', read_only=True)

    class Meta:
        model = ReferralHistory
        fields = [
            'id', 'referrer_email', 'referred_email',
            'referrer_reward_issued', 'referrer_points_earned',
            'referred_reward_issued', 'qualifying_order',
            'created_at'
        ]


class ReferralLinkSerializer(serializers.Serializer):
    """Serializer for referral link response."""

    referral_code = serializers.CharField()
    referral_url = serializers.URLField()
    total_referrals = serializers.IntegerField()
    pending_rewards = serializers.IntegerField()
    earned_points = serializers.IntegerField()


class ApplyReferralSerializer(serializers.Serializer):
    """Serializer for applying referral code."""

    code = serializers.CharField()

    def validate_code(self, value):
        """Validate referral code exists and is not user's own code."""
        from apps.accounts.models import CustomerProfile

        try:
            profile = CustomerProfile.objects.get(referral_code=value.upper())
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid referral code.")

        # Check if user is trying to use their own code
        user = self.context.get('request')
        if user and hasattr(user, 'user'):
            if hasattr(user.user, 'profile') and user.user.profile.referral_code == value.upper():
                raise serializers.ValidationError("You cannot use your own referral code.")

        return value.upper()
