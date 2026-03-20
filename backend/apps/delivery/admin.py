"""
Admin configuration for delivery app.
"""

from django.contrib import admin
from .models import DeliveryZone, DeliveryWindow, DriverAssignment, RouteSummary


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    """Admin for delivery zones."""

    list_display = [
        'postal_code_prefix', 'label', 'city', 'delivery_fee',
        'free_delivery_threshold', 'is_active', 'priority'
    ]
    list_filter = ['is_active', 'city']
    search_fields = ['postal_code_prefix', 'label']
    ordering = ['priority', 'postal_code_prefix']


@admin.register(DeliveryWindow)
class DeliveryWindowAdmin(admin.ModelAdmin):
    """Admin for delivery windows."""

    list_display = [
        'date', 'display_time', 'current_orders', 'max_orders',
        'spots_remaining', 'is_open', 'cutoff_datetime'
    ]
    list_filter = ['is_open', 'date']
    search_fields = ['date']
    date_hierarchy = 'date'
    filter_horizontal = ['zones']

    def spots_remaining(self, obj):
        return obj.spots_remaining
    spots_remaining.short_description = 'Spots Left'

    def display_time(self, obj):
        return obj.display_time
    display_time.short_description = 'Time Window'


@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    """Admin for driver assignments."""

    list_display = [
        'order', 'driver', 'status', 'route_order',
        'assigned_at', 'delivered_at'
    ]
    list_filter = ['status', 'assigned_at', 'driver']
    search_fields = ['order__order_number', 'driver__email']
    readonly_fields = ['assigned_at']
    date_hierarchy = 'assigned_at'

    fieldsets = (
        ('Assignment', {
            'fields': ('order', 'driver', 'status', 'route_order')
        }),
        ('Timing', {
            'fields': ('assigned_at', 'picked_up_at', 'delivered_at', 'estimated_arrival')
        }),
        ('Notes', {
            'fields': ('driver_notes', 'delivery_photo_url', 'customer_feedback')
        }),
    )


@admin.register(RouteSummary)
class RouteSummaryAdmin(admin.ModelAdmin):
    """Admin for route summaries."""

    list_display = [
        'driver', 'date', 'total_orders', 'completed_orders',
        'failed_orders', 'route_started_at', 'route_completed_at'
    ]
    list_filter = ['date', 'driver']
    search_fields = ['driver__email']
    date_hierarchy = 'date'
