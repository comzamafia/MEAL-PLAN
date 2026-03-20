"""
Tests for Orders app — models and API endpoints.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from django.utils import timezone

from apps.orders.models import Order, OrderItem, Subscription, SubscriptionItem


# ─── Model Tests ────────────────────────────────────────────────────────────

class TestOrderModel:
    def test_str(self, customer_user, menu_item):
        order = Order.objects.create(
            order_number='WMP-20260319-0001',
            customer=customer_user,
            subtotal=Decimal('14.99'),
            total=Decimal('16.94'),
            delivery_date=date.today(),
        )
        assert str(order) == 'Order WMP-20260319-0001'

    def test_auto_order_number(self, customer_user):
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('29.98'),
            total=Decimal('33.88'),
            delivery_date=date.today(),
        )
        assert order.order_number.startswith('WMP-')
        assert len(order.order_number) == 17  # WMP-YYYYMMDD-XXXX

    def test_default_status_is_pending(self, customer_user):
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('10.00'),
            total=Decimal('11.30'),
            delivery_date=date.today(),
        )
        assert order.status == 'pending'

    def test_default_tax_type_is_hst(self, customer_user):
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('10.00'),
            total=Decimal('11.30'),
            delivery_date=date.today(),
        )
        assert order.tax_type == 'HST'
        assert order.tax_rate == Decimal('0.13')

    def test_ordering_by_created_at(self, customer_user):
        o1 = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('10.00'),
            total=Decimal('11.30'),
            delivery_date=date.today(),
        )
        o2 = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('20.00'),
            total=Decimal('22.60'),
            delivery_date=date.today(),
        )
        orders = list(Order.objects.all())
        assert orders[0] == o2  # most recent first


class TestOrderItemModel:
    def test_str(self, customer_user, menu_item):
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('14.99'),
            total=Decimal('16.94'),
            delivery_date=date.today(),
        )
        item = OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=2,
            unit_price=Decimal('14.99'),
        )
        assert str(item) == '2x Pad Thai'

    def test_subtotal_property(self, customer_user, menu_item):
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('29.98'),
            total=Decimal('33.88'),
            delivery_date=date.today(),
        )
        item = OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=3,
            unit_price=Decimal('14.99'),
            modifiers_total=Decimal('2.00'),
        )
        assert item.subtotal == Decimal('50.97')  # (14.99 + 2.00) * 3


class TestSubscriptionModel:
    def test_str(self, customer_user):
        sub = Subscription.objects.create(
            customer=customer_user,
            plan_type='standard',
            price_per_cycle=Decimal('89.99'),
            next_billing_date=date.today() + timedelta(days=7),
        )
        assert 'standard' in str(sub)
        assert customer_user.email in str(sub)

    def test_default_status_active(self, customer_user):
        sub = Subscription.objects.create(
            customer=customer_user,
            plan_type='starter',
            price_per_cycle=Decimal('49.99'),
            next_billing_date=date.today() + timedelta(days=7),
        )
        assert sub.status == 'active'

    def test_plan_types(self, customer_user):
        for plan, price in [('starter', '49.99'), ('standard', '89.99'), ('premium', '119.99')]:
            sub = Subscription.objects.create(
                customer=customer_user,
                plan_type=plan,
                price_per_cycle=Decimal(price),
                next_billing_date=date.today() + timedelta(days=7),
            )
            assert sub.plan_type == plan


class TestSubscriptionItemModel:
    def test_str(self, customer_user, menu_item):
        sub = Subscription.objects.create(
            customer=customer_user,
            plan_type='standard',
            price_per_cycle=Decimal('89.99'),
            next_billing_date=date.today() + timedelta(days=7),
        )
        item = SubscriptionItem.objects.create(
            subscription=sub,
            menu_item=menu_item,
            quantity=2,
            week_number=1,
        )
        assert '2x Pad Thai' in str(item)
        assert 'Week 1' in str(item)


# ─── API Tests ──────────────────────────────────────────────────────────────

class TestCreatePaymentIntentAPI:
    def test_empty_cart_returns_400(self, api_client):
        res = api_client.post('/api/v1/checkout/create-intent/', {'items': []}, format='json')
        assert res.status_code == 400

    def test_valid_cart_returns_client_secret(self, api_client, menu_item):
        res = api_client.post('/api/v1/checkout/create-intent/', {
            'items': [{'menu_item_id': str(menu_item.id), 'quantity': 2}],
        }, format='json')
        assert res.status_code == 200
        assert 'client_secret' in res.data['data']
        assert Decimal(res.data['data']['subtotal']) == Decimal('29.98')

    def test_coupon_applied(self, api_client, menu_item, coupon):
        res = api_client.post('/api/v1/checkout/create-intent/', {
            'items': [{'menu_item_id': str(menu_item.id), 'quantity': 6}],
            'coupon_code': 'WELCOME15',
        }, format='json')
        assert res.status_code == 200
        assert Decimal(res.data['data']['discount']) > Decimal('0.00')


class TestConfirmOrderAPI:
    def test_confirm_creates_order(self, auth_client, menu_item):
        res = auth_client.post('/api/v1/checkout/confirm/', {
            'payment_intent_id': 'pi_test_123',
            'items': [{'menu_item_id': str(menu_item.id), 'quantity': 1}],
            'delivery_address': {'street_address': '123 Main St', 'city': 'Oakville'},
        }, format='json')
        assert res.status_code == 200
        assert 'order_number' in res.data['data']
        assert Order.objects.filter(
            order_number=res.data['data']['order_number']
        ).exists()

    def test_confirm_awards_loyalty_points(self, auth_client, customer_user, menu_item):
        profile = customer_user.profile
        initial_points = profile.wela_points_balance

        auth_client.post('/api/v1/checkout/confirm/', {
            'payment_intent_id': 'pi_test_456',
            'items': [{'menu_item_id': str(menu_item.id), 'quantity': 1}],
            'delivery_address': {'street_address': '123 Main St'},
        }, format='json')

        profile.refresh_from_db()
        assert profile.wela_points_balance > initial_points

    def test_confirm_with_coupon_increments_usage(self, auth_client, menu_item, coupon):
        initial_uses = coupon.current_uses
        auth_client.post('/api/v1/checkout/confirm/', {
            'payment_intent_id': 'pi_test_789',
            'items': [{'menu_item_id': str(menu_item.id), 'quantity': 1}],
            'coupon_code': 'WELCOME15',
            'delivery_address': {'street_address': '456 Oak Ave'},
        }, format='json')
        coupon.refresh_from_db()
        assert coupon.current_uses == initial_uses + 1


class TestOTOUpsellAPI:
    def test_unauthenticated_returns_401(self, api_client):
        res = api_client.post('/api/v1/checkout/oto/', {'plan_type': 'standard'}, format='json')
        assert res.status_code == 401

    def test_creates_subscription(self, auth_client, customer_user):
        res = auth_client.post('/api/v1/checkout/oto/', {'plan_type': 'premium'}, format='json')
        assert res.status_code == 200
        assert res.data['data']['plan'] == 'premium'
        assert Subscription.objects.filter(customer=customer_user, plan_type='premium').exists()


class TestSubscriptionManagementAPI:
    @pytest.fixture
    def active_subscription(self, customer_user):
        return Subscription.objects.create(
            customer=customer_user,
            plan_type='standard',
            price_per_cycle=Decimal('89.99'),
            next_billing_date=date.today() + timedelta(days=7),
            status='active',
        )

    def test_pause_subscription(self, auth_client, active_subscription):
        pause_date = (date.today() + timedelta(days=14)).isoformat()
        res = auth_client.post('/api/v1/subscriptions/pause/', {
            'pause_until_date': pause_date,
        }, format='json')
        assert res.status_code == 200
        active_subscription.refresh_from_db()
        assert active_subscription.status == 'paused'

    def test_resume_subscription(self, auth_client, active_subscription):
        active_subscription.status = 'paused'
        active_subscription.save()
        res = auth_client.post('/api/v1/subscriptions/resume/', format='json')
        assert res.status_code == 200
        active_subscription.refresh_from_db()
        assert active_subscription.status == 'active'

    def test_resume_no_paused_sub_returns_404(self, auth_client, active_subscription):
        res = auth_client.post('/api/v1/subscriptions/resume/', format='json')
        assert res.status_code == 404

    def test_cancel_subscription(self, auth_client, active_subscription):
        res = auth_client.post('/api/v1/subscriptions/cancel/', {
            'reason': 'Too expensive',
        }, format='json')
        assert res.status_code == 200
        active_subscription.refresh_from_db()
        assert active_subscription.status == 'cancelled'
        assert active_subscription.cancellation_reason == 'Too expensive'

    def test_skip_week(self, auth_client, active_subscription):
        skip_date = (date.today() + timedelta(days=7)).isoformat()
        res = auth_client.post('/api/v1/subscriptions/skip-week/', {
            'week_date': skip_date,
        }, format='json')
        assert res.status_code == 200
        active_subscription.refresh_from_db()
        assert skip_date in active_subscription.skipped_weeks

    def test_skip_week_idempotent(self, auth_client, active_subscription):
        skip_date = (date.today() + timedelta(days=7)).isoformat()
        auth_client.post('/api/v1/subscriptions/skip-week/', {'week_date': skip_date}, format='json')
        auth_client.post('/api/v1/subscriptions/skip-week/', {'week_date': skip_date}, format='json')
        active_subscription.refresh_from_db()
        assert active_subscription.skipped_weeks.count(skip_date) == 1


class TestCustomerOrderListAPI:
    def test_unauthenticated_returns_401(self, api_client):
        res = api_client.get('/api/v1/checkout/my/')
        assert res.status_code == 401

    def test_returns_own_orders(self, auth_client, customer_user, menu_item):
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('14.99'),
            total=Decimal('16.94'),
            delivery_date=date.today(),
            status='confirmed',
        )
        res = auth_client.get('/api/v1/checkout/my/')
        assert res.status_code == 200
        assert len(res.data['data']) == 1
        assert res.data['data'][0]['order_number'] == order.order_number


class TestCustomerSubscriptionAPI:
    def test_unauthenticated_returns_401(self, api_client):
        res = api_client.get('/api/v1/subscriptions/current/')
        assert res.status_code == 401

    def test_no_subscription_returns_null(self, auth_client):
        res = auth_client.get('/api/v1/subscriptions/current/')
        assert res.status_code == 200
        assert res.data['data'] is None

    def test_returns_active_subscription(self, auth_client, customer_user):
        sub = Subscription.objects.create(
            customer=customer_user,
            plan_type='standard',
            price_per_cycle=Decimal('89.99'),
            next_billing_date=date.today() + timedelta(days=7),
            status='active',
        )
        res = auth_client.get('/api/v1/subscriptions/current/')
        assert res.status_code == 200
        assert res.data['data']['plan_type'] == 'standard'
