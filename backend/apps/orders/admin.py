"""
Admin configuration for orders app.
"""

from django.contrib import admin
from .models import Order, OrderItem, Subscription, SubscriptionItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ['menu_item', 'quantity', 'unit_price', 'modifiers_total', 'subtotal']

    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for orders."""

    list_display = [
        'order_number', 'customer', 'status', 'total', 'delivery_date',
        'created_at'
    ]
    list_filter = ['status', 'delivery_date', 'created_at']
    search_fields = ['order_number', 'customer__email', 'stripe_payment_intent_id']
    readonly_fields = [
        'order_number', 'subtotal', 'discount_amount', 'delivery_fee',
        'tax_amount', 'total', 'points_earned', 'points_redeemed',
        'stripe_payment_intent_id', 'stripe_charge_id',
        'created_at', 'updated_at', 'confirmed_at', 'delivered_at'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'delivery_date'

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'customer', 'status')
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'delivery_date', 'delivery_window', 'delivery_address_snapshot')
        }),
        ('Pricing', {
            'fields': (
                'subtotal', 'discount_amount', 'delivery_fee',
                'tax_rate', 'tax_amount', 'tax_type', 'total'
            )
        }),
        ('Loyalty', {
            'fields': ('points_earned', 'points_redeemed', 'points_redemption_value', 'coupon')
        }),
        ('Stripe', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [OrderItemInline]

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of orders - soft delete only
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for order items."""

    list_display = ['order', 'menu_item', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['order__status', 'order__delivery_date']
    search_fields = ['order__order_number', 'menu_item__name_en']

    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"


class SubscriptionItemInline(admin.TabularInline):
    """Inline admin for subscription items."""
    model = SubscriptionItem
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for subscriptions."""

    list_display = [
        'customer', 'plan_type', 'status', 'billing_cycle',
        'next_billing_date', 'price_per_cycle'
    ]
    list_filter = ['status', 'plan_type', 'billing_cycle']
    search_fields = ['customer__email', 'stripe_subscription_id']
    readonly_fields = ['stripe_subscription_id', 'stripe_customer_id', 'created_at', 'updated_at']
    date_hierarchy = 'next_billing_date'

    fieldsets = (
        ('Subscription Info', {
            'fields': ('customer', 'plan_type', 'billing_cycle', 'status')
        }),
        ('Billing', {
            'fields': ('price_per_cycle', 'next_billing_date', 'last_billing_date')
        }),
        ('Benefits', {
            'fields': ('free_delivery', 'discount_percentage')
        }),
        ('Pause/Skip', {
            'fields': ('pause_until_date', 'skipped_weeks')
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Stripe', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Delivery', {
            'fields': ('delivery_address',)
        }),
    )

    inlines = [SubscriptionItemInline]
