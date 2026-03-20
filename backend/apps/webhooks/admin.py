from django.contrib import admin
from .models import StripeWebhookEvent


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ['stripe_event_id', 'event_type', 'status', 'received_at', 'processed_at']
    list_filter = ['status', 'event_type']
    search_fields = ['stripe_event_id', 'event_type']
    readonly_fields = [
        'id', 'stripe_event_id', 'event_type', 'api_version',
        'payload', 'status', 'processing_error', 'retry_count',
        'related_order_id', 'related_subscription_id',
        'received_at', 'processed_at',
    ]
    date_hierarchy = 'received_at'
    ordering = ['-received_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
