"""
User and Account models for Wela Meal Plan.

Includes:
- Custom User model with role-based access
- CustomerProfile with preferences and Wela Points
- DeliveryAddress for multiple saved addresses
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control.

    Roles:
    - customer: Regular customer placing orders
    - admin: Full system access
    - kitchen_staff: Access to prep lists and recipes
    - driver: Access to delivery routes and status updates
    """

    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        ADMIN = 'admin', 'Admin'
        KITCHEN_STAFF = 'kitchen_staff', 'Kitchen Staff'
        DRIVER = 'driver', 'Driver'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['stripe_customer_id']),
        ]

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_staff_role(self):
        return self.role in [self.Role.ADMIN, self.Role.KITCHEN_STAFF]


class CustomerProfile(models.Model):
    """
    Extended profile for customers with preferences and loyalty data.
    """

    class Language(models.TextChoices):
        EN = 'en', 'English'
        TH = 'th', 'Thai'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )

    # Loyalty
    wela_points_balance = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )

    # Preferences
    preferred_language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.EN
    )
    email_marketing_opt_in = models.BooleanField(default=False)
    email_marketing_consent_at = models.DateTimeField(null=True, blank=True)
    sms_opt_in = models.BooleanField(default=False)
    sms_consent_at = models.DateTimeField(null=True, blank=True)

    # Dietary preferences (for personalized recommendations)
    dietary_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_profiles'

    def __str__(self):
        return f"Profile: {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)

    def _generate_referral_code(self):
        """Generate a unique referral code."""
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while CustomerProfile.objects.filter(referral_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return code


class DeliveryAddress(models.Model):
    """
    Customer's saved delivery addresses.
    Supports multiple addresses per customer with one default.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_addresses'
    )

    label = models.CharField(max_length=50, default='Home')  # e.g., "Home", "Office"
    recipient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    street_address = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, blank=True)  # Apt/Suite number
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=50, default='Ontario')
    postal_code = models.CharField(max_length=10, db_index=True)
    country = models.CharField(max_length=50, default='Canada')

    delivery_instructions = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_addresses'
        verbose_name_plural = 'Delivery addresses'
        indexes = [
            models.Index(fields=['customer', 'is_default']),
            models.Index(fields=['postal_code']),
        ]

    def __str__(self):
        return f"{self.label}: {self.street_address}, {self.city}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per customer
        if self.is_default:
            DeliveryAddress.objects.filter(
                customer=self.customer,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        parts = [self.street_address]
        if self.unit:
            parts.append(f"Unit {self.unit}")
        parts.append(f"{self.city}, {self.province} {self.postal_code}")
        return ', '.join(parts)
