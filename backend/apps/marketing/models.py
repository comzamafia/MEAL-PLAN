"""
Marketing and Loyalty models for Wela Meal Plan.

Includes:
- Coupon: Discount codes with various rules
- LoyaltyPoint: Wela Points ledger for earn/spend
- ReferralHistory: Track referral rewards
"""

import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Coupon(models.Model):
    """
    Discount coupon codes with flexible rules.
    """

    class DiscountType(models.TextChoices):
        PERCENT = 'percent', 'Percentage Off'
        FIXED = 'fixed', 'Fixed Amount Off'
        FREE_DELIVERY = 'free_delivery', 'Free Delivery'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)

    # Discount
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Limits
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    current_uses = models.PositiveIntegerField(default=0)
    max_uses_per_customer = models.PositiveIntegerField(default=1)

    # Conditions
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cap on discount amount (for percentage discounts)"
    )
    is_first_order_only = models.BooleanField(default=False)
    is_subscription_only = models.BooleanField(default=False)

    # Validity
    start_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coupons'
        indexes = [
            models.Index(fields=['code', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} ({self.discount_type})"

    @property
    def is_valid(self):
        """Check if coupon is currently valid (ignoring customer-specific rules)."""
        from django.utils import timezone
        now = timezone.now()

        if not self.is_active:
            return False

        if self.max_uses and self.current_uses >= self.max_uses:
            return False

        if self.start_date and now < self.start_date:
            return False

        if self.expiry_date and now > self.expiry_date:
            return False

        return True

    def calculate_discount(self, order_subtotal, delivery_fee=Decimal('0.00')):
        """Calculate the discount amount for an order."""
        if self.discount_type == self.DiscountType.PERCENT:
            discount = order_subtotal * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount

        elif self.discount_type == self.DiscountType.FIXED:
            return min(self.discount_value, order_subtotal)

        elif self.discount_type == self.DiscountType.FREE_DELIVERY:
            return delivery_fee

        return Decimal('0.00')


class CouponUsage(models.Model):
    """Track which customers have used which coupons."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupon_usages'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        related_name='coupon_usage'
    )
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coupon_usages'

    def __str__(self):
        return f"{self.customer.email} used {self.coupon.code}"


class LoyaltyPoint(models.Model):
    """
    Wela Points ledger - full transaction history for earn/spend.
    """

    class Reason(models.TextChoices):
        ORDER_EARNED = 'order_earned', 'Points Earned from Order'
        ORDER_REDEEMED = 'order_redeemed', 'Points Redeemed for Discount'
        REFERRAL_BONUS = 'referral_bonus', 'Referral Bonus'
        SIGNUP_BONUS = 'signup_bonus', 'Sign-up Bonus'
        ADMIN_ADJUSTMENT = 'admin_adjustment', 'Admin Adjustment'
        REFUND_DEDUCTION = 'refund_deduction', 'Points Deducted (Order Refund)'
        EXPIRY = 'expiry', 'Points Expired'
        PROMOTIONAL = 'promotional', 'Promotional Bonus'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty_points'
    )

    # Points change (positive = earned, negative = spent/deducted)
    points_delta = models.IntegerField()
    balance_after = models.IntegerField()
    reason = models.CharField(max_length=30, choices=Reason.choices)
    description = models.TextField(blank=True)

    # Linked order (if applicable)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_transactions'
    )

    # Admin who made the adjustment (if applicable)
    adjusted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_adjustments'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loyalty_points'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
        ]

    def __str__(self):
        sign = '+' if self.points_delta > 0 else ''
        return f"{self.customer.email}: {sign}{self.points_delta} pts ({self.reason})"


class ReferralHistory(models.Model):
    """
    Track referral relationships and reward status.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referrals_made'
    )
    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_source'
    )

    # Reward tracking
    referrer_reward_issued = models.BooleanField(default=False)
    referrer_reward_issued_at = models.DateTimeField(null=True, blank=True)
    referrer_points_earned = models.PositiveIntegerField(default=0)

    referred_reward_issued = models.BooleanField(default=False)
    referred_discount_code = models.CharField(max_length=50, blank=True)

    # Qualifying order
    qualifying_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="First qualifying order from referred user"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'referral_history'
        indexes = [
            models.Index(fields=['referrer', 'referrer_reward_issued']),
        ]

    def __str__(self):
        return f"{self.referrer.email} referred {self.referred_user.email}"


# =============================================================================
# Constants and Configuration
# =============================================================================

# Wela Points conversion rate: 100 points = $1
POINTS_TO_DOLLAR_RATE = 100

# Points earned per dollar spent
POINTS_EARN_RATE = 10  # 10 points per $1 = 10% back

# Referral rewards
REFERRAL_POINTS_REWARD = 500  # 500 points = $5 for referrer
REFERRAL_DISCOUNT_PERCENT = 15  # 15% off first order for referred user
