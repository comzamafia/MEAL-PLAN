"""
Webhook event models for Wela Meal Plan.

Tracks all incoming Stripe webhook events for idempotency
and debugging purposes.
"""

import uuid
from django.db import models


class StripeWebhookEvent(models.Model):
    """
    Records all Stripe webhook events received.
    Used for idempotency (preventing double-processing) and debugging.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        PROCESSED = 'processed', 'Processed'
        FAILED = 'failed', 'Failed'
        IGNORED = 'ignored', 'Ignored'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Stripe event data
    stripe_event_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=100, db_index=True)
    api_version = models.CharField(max_length=20, blank=True)

    # Raw payload (for debugging/replay)
    payload = models.JSONField()

    # Processing status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    processing_error = models.TextField(blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)

    # Linked objects (populated after processing)
    related_order_id = models.UUIDField(null=True, blank=True, db_index=True)
    related_subscription_id = models.UUIDField(null=True, blank=True, db_index=True)

    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'stripe_webhook_events'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['event_type', 'status']),
            models.Index(fields=['received_at']),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.stripe_event_id[:20]}...)"

    def mark_processed(self):
        """Mark event as successfully processed."""
        from django.utils import timezone
        self.status = self.Status.PROCESSED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def mark_failed(self, error_message):
        """Mark event as failed with error message."""
        self.status = self.Status.FAILED
        self.processing_error = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'processing_error', 'retry_count'])

    def mark_ignored(self, reason=''):
        """Mark event as ignored (not relevant for processing)."""
        self.status = self.Status.IGNORED
        self.processing_error = reason
        self.save(update_fields=['status', 'processing_error'])
