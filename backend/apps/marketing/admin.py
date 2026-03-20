"""
Admin configuration for marketing app.
"""

from django.contrib import admin
from .models import Coupon, CouponUsage, LoyaltyPoint, ReferralHistory


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin for coupons."""

    list_display = [
        'code', 'discount_type', 'discount_value', 'current_uses',
        'max_uses', 'is_active', 'expiry_date'
    ]
    list_filter = ['discount_type', 'is_active', 'is_first_order_only', 'is_subscription_only']
    search_fields = ['code', 'description']
    readonly_fields = ['current_uses', 'created_at', 'updated_at']

    fieldsets = (
        ('Coupon Info', {
            'fields': ('code', 'description')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'max_discount_amount')
        }),
        ('Limits', {
            'fields': ('max_uses', 'current_uses', 'max_uses_per_customer', 'min_order_amount')
        }),
        ('Conditions', {
            'fields': ('is_first_order_only', 'is_subscription_only')
        }),
        ('Validity', {
            'fields': ('start_date', 'expiry_date', 'is_active')
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """Admin for coupon usage tracking."""

    list_display = ['coupon', 'customer', 'order', 'discount_applied', 'used_at']
    list_filter = ['coupon', 'used_at']
    search_fields = ['coupon__code', 'customer__email']
    readonly_fields = ['used_at']


@admin.register(LoyaltyPoint)
class LoyaltyPointAdmin(admin.ModelAdmin):
    """Admin for loyalty points ledger."""

    list_display = ['customer', 'points_delta', 'balance_after', 'reason', 'order', 'created_at']
    list_filter = ['reason', 'created_at']
    search_fields = ['customer__email', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def has_change_permission(self, request, obj=None):
        # Points ledger is immutable
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReferralHistory)
class ReferralHistoryAdmin(admin.ModelAdmin):
    """Admin for referral tracking."""

    list_display = [
        'referrer', 'referred_user', 'referrer_reward_issued',
        'referrer_points_earned', 'qualifying_order', 'created_at'
    ]
    list_filter = ['referrer_reward_issued', 'referred_reward_issued', 'created_at']
    search_fields = ['referrer__email', 'referred_user__email']
    readonly_fields = ['created_at', 'updated_at']
