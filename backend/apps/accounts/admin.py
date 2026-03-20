"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile, DeliveryAddress


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""

    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'stripe_customer_id')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'email')}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin for CustomerProfile."""

    list_display = ['user', 'wela_points_balance', 'referral_code', 'preferred_language', 'email_marketing_opt_in']
    list_filter = ['preferred_language', 'email_marketing_opt_in', 'sms_opt_in']
    search_fields = ['user__email', 'referral_code']
    readonly_fields = ['referral_code', 'created_at', 'updated_at']


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    """Admin for DeliveryAddress."""

    list_display = ['customer', 'label', 'city', 'postal_code', 'is_default']
    list_filter = ['city', 'is_default']
    search_fields = ['customer__email', 'street_address', 'postal_code']
