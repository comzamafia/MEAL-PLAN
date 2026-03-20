"""
Delivery and Route models for Wela Meal Plan.

Includes:
- DeliveryZone: Serviceable postal code areas with fees
- DeliveryWindow: Time slots and capacity management
- DriverAssignment: Order-to-driver assignments
"""

import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models


class DeliveryZone(models.Model):
    """
    Serviceable delivery zones based on postal code prefixes.
    Used for validating delivery addresses and calculating fees.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Postal code matching (e.g., "L6H" for Oakville)
    postal_code_prefix = models.CharField(max_length=10, unique=True, db_index=True)
    label = models.CharField(max_length=100)  # e.g., "Oakville North", "Burlington East"
    city = models.CharField(max_length=100, default='Oakville')

    # Fees
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('5.99'))
    free_delivery_threshold = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('75.00'),
        help_text="Order subtotal for free delivery"
    )

    # Availability
    is_active = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(default=0, help_text="Lower = higher priority")

    # Notes
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_zones'
        ordering = ['priority', 'label']

    def __str__(self):
        return f"{self.postal_code_prefix} - {self.label}"

    def get_delivery_fee(self, order_subtotal):
        """Calculate delivery fee based on order subtotal."""
        if order_subtotal >= self.free_delivery_threshold:
            return Decimal('0.00')
        return self.delivery_fee


class DeliveryWindow(models.Model):
    """
    Delivery time slots with capacity management.
    Controls when customers can receive deliveries.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    date = models.DateField(db_index=True)
    time_start = models.TimeField()
    time_end = models.TimeField()

    # Capacity
    max_orders = models.PositiveIntegerField(default=50)
    current_orders = models.PositiveIntegerField(default=0)

    # Availability
    is_open = models.BooleanField(default=True)

    # Cut-off (orders must be placed before this time)
    cutoff_datetime = models.DateTimeField(null=True, blank=True)

    # Zone restrictions (optional - if blank, available for all zones)
    zones = models.ManyToManyField(
        DeliveryZone,
        blank=True,
        related_name='delivery_windows'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_windows'
        ordering = ['date', 'time_start']
        unique_together = ['date', 'time_start', 'time_end']

    def __str__(self):
        return f"{self.date} {self.time_start}-{self.time_end}"

    @property
    def is_available(self):
        """Check if window is available for new orders."""
        from django.utils import timezone

        if not self.is_open:
            return False

        if self.current_orders >= self.max_orders:
            return False

        # Check cutoff
        if self.cutoff_datetime and timezone.now() > self.cutoff_datetime:
            return False

        return True

    @property
    def spots_remaining(self):
        return max(0, self.max_orders - self.current_orders)

    @property
    def display_time(self):
        """Format time window for display."""
        start = self.time_start.strftime('%H:%M')
        end = self.time_end.strftime('%H:%M')
        return f"{start} - {end}"


class DriverAssignment(models.Model):
    """
    Assigns orders to delivery drivers with status tracking.
    """

    class Status(models.TextChoices):
        ASSIGNED = 'assigned', 'Assigned'
        PICKED_UP = 'picked_up', 'Picked Up'
        IN_TRANSIT = 'in_transit', 'In Transit'
        DELIVERED = 'delivered', 'Delivered'
        FAILED = 'failed', 'Delivery Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='driver_assignment'
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deliveries'
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED
    )

    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Route optimization
    route_order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Order in delivery route (lower = earlier)"
    )
    estimated_arrival = models.DateTimeField(null=True, blank=True)

    # Notes
    driver_notes = models.TextField(blank=True)
    delivery_photo_url = models.URLField(max_length=500, blank=True)
    customer_feedback = models.TextField(blank=True)

    class Meta:
        db_table = 'driver_assignments'
        ordering = ['route_order']
        indexes = [
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['assigned_at']),
        ]

    def __str__(self):
        return f"{self.order.order_number} -> {self.driver.get_full_name() if self.driver else 'Unassigned'}"


class RouteSummary(models.Model):
    """
    Daily route summary for drivers.
    Aggregates all assignments for a given date.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='route_summaries'
    )
    date = models.DateField(db_index=True)

    # Statistics
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    failed_orders = models.PositiveIntegerField(default=0)

    # Timing
    route_started_at = models.DateTimeField(null=True, blank=True)
    route_completed_at = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'route_summaries'
        unique_together = ['driver', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Route: {self.driver.get_full_name()} on {self.date}"
