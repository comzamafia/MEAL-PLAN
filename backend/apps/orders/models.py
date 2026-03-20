"""
Order and Subscription models for Wela Meal Plan.

Includes:
- Order: One-time and subscription orders
- OrderItem: Line items with modifier snapshots
- Subscription: Recurring delivery plans
- SubscriptionItem: Items in subscription plan
"""

import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class Order(models.Model):
    """
    Customer order with full order lifecycle tracking.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Payment'
        CONFIRMED = 'confirmed', 'Payment Confirmed'
        PREP = 'prep', 'In Preparation'
        READY = 'ready', 'Ready for Delivery'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'
        FAILED = 'failed', 'Payment Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, db_index=True)

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    delivery_address = models.ForeignKey(
        'accounts.DeliveryAddress',
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))

    # Canadian Tax (HST for Ontario)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.13'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_type = models.CharField(max_length=10, default='HST')

    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Wela Points
    points_earned = models.PositiveIntegerField(default=0)
    points_redeemed = models.PositiveIntegerField(default=0)
    points_redemption_value = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    # Coupon
    coupon = models.ForeignKey(
        'marketing.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    # Delivery scheduling
    delivery_date = models.DateField(db_index=True)
    delivery_window = models.ForeignKey(
        'delivery.DeliveryWindow',
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )

    # Order lifecycle
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)

    # Subscription link (if this order is part of a subscription)
    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # Address snapshot (preserved at order time)
    delivery_address_snapshot = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['delivery_date', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """Generate unique order number: WMP-YYYYMMDD-XXXX"""
        from django.utils import timezone
        import random
        today = timezone.now().strftime('%Y%m%d')
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"WMP-{today}-{suffix}"

    def calculate_totals(self):
        """Recalculate subtotal, tax, and total."""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        taxable_amount = self.subtotal - self.discount_amount + self.delivery_fee - self.points_redemption_value
        self.tax_amount = (taxable_amount * self.tax_rate).quantize(Decimal('0.01'))
        self.total = taxable_amount + self.tax_amount


class OrderItem(models.Model):
    """
    Individual line items in an order.
    Stores modifier snapshot at order time to preserve history.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    # Modifier snapshot (stored as JSON at order time)
    modifiers_snapshot = models.JSONField(
        default=list,
        blank=True,
        help_text="Snapshot of selected modifiers at order time"
    )
    modifiers_total = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    # Menu item snapshot (name, nutrition at order time)
    item_snapshot = models.JSONField(
        null=True,
        blank=True,
        help_text="Snapshot of item details at order time"
    )

    special_instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name_en}"

    @property
    def subtotal(self):
        return (self.unit_price + self.modifiers_total) * self.quantity


class Subscription(models.Model):
    """
    Customer subscription for recurring meal deliveries.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        CANCELLED = 'cancelled', 'Cancelled'
        PAST_DUE = 'past_due', 'Past Due'
        TRIAL = 'trial', 'Trial'

    class BillingCycle(models.TextChoices):
        WEEKLY = 'weekly', 'Weekly'
        BIWEEKLY = 'biweekly', 'Every 2 Weeks'
        MONTHLY = 'monthly', 'Monthly'

    class PlanType(models.TextChoices):
        STARTER = 'starter', '5 Meals/Week'
        STANDARD = 'standard', '10 Meals/Week'
        PREMIUM = 'premium', '15 Meals/Week'
        CUSTOM = 'custom', 'Custom Plan'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    # Subscription plan
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.WEEKLY
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    # Billing
    next_billing_date = models.DateField(db_index=True)
    last_billing_date = models.DateField(null=True, blank=True)
    price_per_cycle = models.DecimalField(max_digits=10, decimal_places=2)

    # Stripe
    stripe_subscription_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    # Pause/Skip
    pause_until_date = models.DateField(null=True, blank=True)
    skipped_weeks = models.JSONField(default=list, blank=True)

    # Cancellation
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Default delivery
    delivery_address = models.ForeignKey(
        'accounts.DeliveryAddress',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions'
    )

    # Benefits
    free_delivery = models.BooleanField(default=False)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['next_billing_date', 'status']),
            models.Index(fields=['stripe_subscription_id']),
        ]

    def __str__(self):
        return f"Subscription {self.plan_type} - {self.customer.email}"


class SubscriptionItem(models.Model):
    """
    Items included in a subscription plan for each week.
    Customer can customize their weekly selections.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.CASCADE,
        related_name='subscription_items'
    )
    quantity = models.PositiveIntegerField(default=1)

    # Which week of the rotation
    week_number = models.PositiveSmallIntegerField(default=1)

    # Selected modifiers
    modifiers = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_items'

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name_en} (Week {self.week_number})"
