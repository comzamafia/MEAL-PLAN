"""
Tests for Webhooks app — StripeWebhookEvent model and admin.
"""

import pytest
from decimal import Decimal
from datetime import date

from apps.webhooks.models import StripeWebhookEvent
from apps.orders.models import Order, Subscription


# ─── Model Tests ────────────────────────────────────────────────────────────

class TestStripeWebhookEventModel:
    def test_str(self, db):
        event = StripeWebhookEvent.objects.create(
            stripe_event_id='evt_test_123',
            event_type='payment_intent.succeeded',
            payload={'id': 'evt_test_123'},
        )
        assert 'evt_test_123' in str(event)

    def test_default_status_pending(self, db):
        event = StripeWebhookEvent.objects.create(
            stripe_event_id='evt_test_456',
            event_type='payment_intent.succeeded',
            payload={},
        )
        assert event.status == 'pending'

    def test_ordering_by_received_at(self, db):
        e1 = StripeWebhookEvent.objects.create(
            stripe_event_id='evt_first',
            event_type='payment_intent.succeeded',
            payload={},
        )
        e2 = StripeWebhookEvent.objects.create(
            stripe_event_id='evt_second',
            event_type='payment_intent.failed',
            payload={},
        )
        events = list(StripeWebhookEvent.objects.all())
        assert events[0] == e2  # most recent first


# ─── Admin Tests ────────────────────────────────────────────────────────────

class TestStripeWebhookEventAdmin:
    @pytest.fixture
    def django_admin_client(self, admin_user):
        from django.test import Client
        client = Client()
        client.force_login(admin_user)
        return client

    def test_admin_no_add_permission(self, django_admin_client):
        res = django_admin_client.get('/admin/webhooks/stripewebhookevent/add/')
        assert res.status_code == 403

    def test_admin_list_view(self, django_admin_client, db):
        StripeWebhookEvent.objects.create(
            stripe_event_id='evt_admin_test',
            event_type='charge.refunded',
            payload={},
        )
        res = django_admin_client.get('/admin/webhooks/stripewebhookevent/')
        assert res.status_code == 200
