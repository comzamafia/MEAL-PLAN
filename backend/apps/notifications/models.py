"""
Notification models for persisting user notifications.
"""

import uuid
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    Persistent notification record for user-facing notifications.
    Displayed in dashboard notification bell.
    """

    class Category(models.TextChoices):
        ORDER = 'order', 'Order Update'
        SUBSCRIPTION = 'subscription', 'Subscription'
        DELIVERY = 'delivery', 'Delivery'
        LOYALTY = 'loyalty', 'Loyalty Points'
        REFERRAL = 'referral', 'Referral'
        PROMOTION = 'promotion', 'Promotion'
        SYSTEM = 'system', 'System'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )

    category = models.CharField(max_length=20, choices=Category.choices, default=Category.SYSTEM)
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Link to related object (optional)
    action_url = models.CharField(max_length=500, blank=True)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.email}: {self.title}"

    def mark_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
