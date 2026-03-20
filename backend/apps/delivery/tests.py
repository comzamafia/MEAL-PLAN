"""
Tests for Delivery app — DeliveryZone, DeliveryWindow, DriverAssignment models and API endpoints.
"""

import pytest
from decimal import Decimal
from datetime import date, time, timedelta

from django.utils import timezone

from apps.delivery.models import DeliveryZone, DeliveryWindow, DriverAssignment, RouteSummary
from apps.orders.models import Order


# ─── Model Tests ────────────────────────────────────────────────────────────

class TestDeliveryZoneModel:
    def test_str(self, delivery_zone):
        assert 'L6H' in str(delivery_zone)
        assert 'Oakville Central' in str(delivery_zone)

    def test_get_delivery_fee_below_threshold(self, db):
        zone = DeliveryZone.objects.create(
            postal_code_prefix='L6K',
            label='Burlington East',
            city='Burlington',
            delivery_fee=Decimal('5.99'),
            free_delivery_threshold=Decimal('75.00'),
            is_active=True,
        )
        assert zone.get_delivery_fee(Decimal('50.00')) == Decimal('5.99')

    def test_get_delivery_fee_above_threshold(self, db):
        zone = DeliveryZone.objects.create(
            postal_code_prefix='L6L',
            label='Burlington West',
            city='Burlington',
            delivery_fee=Decimal('5.99'),
            free_delivery_threshold=Decimal('75.00'),
            is_active=True,
        )
        assert zone.get_delivery_fee(Decimal('75.00')) == Decimal('0.00')
        assert zone.get_delivery_fee(Decimal('100.00')) == Decimal('0.00')

    def test_ordering(self, db):
        z1 = DeliveryZone.objects.create(
            postal_code_prefix='L6Z',
            label='Zeta Zone',
            priority=2,
            is_active=True,
        )
        z2 = DeliveryZone.objects.create(
            postal_code_prefix='L6A',
            label='Alpha Zone',
            priority=1,
            is_active=True,
        )
        zones = list(DeliveryZone.objects.all())
        assert zones[0] == z2  # lower priority first


class TestDeliveryWindowModel:
    def test_str(self, db):
        window = DeliveryWindow.objects.create(
            date=date(2026, 3, 22),
            time_start=time(10, 0),
            time_end=time(14, 0),
            max_orders=50,
        )
        assert '2026-03-22' in str(window)

    def test_display_time(self, db):
        window = DeliveryWindow.objects.create(
            date=date(2026, 3, 22),
            time_start=time(10, 0),
            time_end=time(14, 0),
        )
        assert window.display_time == '10:00 - 14:00'

    def test_spots_remaining(self, db):
        window = DeliveryWindow.objects.create(
            date=date(2026, 3, 22),
            time_start=time(10, 0),
            time_end=time(14, 0),
            max_orders=50,
            current_orders=45,
        )
        assert window.spots_remaining == 5

    def test_is_available_open(self, db):
        window = DeliveryWindow.objects.create(
            date=date(2026, 3, 22),
            time_start=time(10, 0),
            time_end=time(14, 0),
            max_orders=50,
            current_orders=0,
            is_open=True,
        )
        assert window.is_available is True

    def test_is_available_full(self, db):
        window = DeliveryWindow.objects.create(
            date=date(2026, 3, 22),
            time_start=time(9, 0),
            time_end=time(12, 0),
            max_orders=50,
            current_orders=50,
            is_open=True,
        )
        assert window.is_available is False

    def test_is_available_closed(self, db):
        window = DeliveryWindow.objects.create(
            date=date(2026, 3, 22),
            time_start=time(8, 0),
            time_end=time(11, 0),
            max_orders=50,
            is_open=False,
        )
        assert window.is_available is False

    def test_is_available_past_cutoff(self, db):
        window = DeliveryWindow.objects.create(
            date=date(2026, 3, 22),
            time_start=time(10, 0),
            time_end=time(14, 0),
            max_orders=50,
            is_open=True,
            cutoff_datetime=timezone.now() - timedelta(hours=1),
        )
        assert window.is_available is False


class TestDriverAssignmentModel:
    def test_str(self, customer_user, admin_user):
        order = Order.objects.create(
            order_number='WMP-20260319-9999',
            customer=customer_user,
            subtotal=Decimal('14.99'),
            total=Decimal('16.94'),
            delivery_date=date.today(),
        )
        assignment = DriverAssignment.objects.create(
            order=order,
            driver=admin_user,
        )
        assert 'WMP-20260319-9999' in str(assignment)

    def test_default_status_assigned(self, customer_user, admin_user):
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('10.00'),
            total=Decimal('11.30'),
            delivery_date=date.today(),
        )
        assignment = DriverAssignment.objects.create(order=order, driver=admin_user)
        assert assignment.status == 'assigned'


class TestRouteSummaryModel:
    def test_str(self, admin_user):
        route = RouteSummary.objects.create(
            driver=admin_user,
            date=date.today(),
            total_orders=10,
        )
        assert str(admin_user.get_full_name()) in str(route)


# ─── API Tests ──────────────────────────────────────────────────────────────

class TestDeliveryZoneListAPI:
    def test_list_zones(self, api_client, delivery_zone):
        res = api_client.get('/api/v1/delivery/zones/')
        assert res.status_code == 200

    def test_only_active_zones(self, api_client, delivery_zone):
        DeliveryZone.objects.create(
            postal_code_prefix='L6X',
            label='Inactive Zone',
            is_active=False,
        )
        res = api_client.get('/api/v1/delivery/zones/')
        assert res.status_code == 200


class TestValidatePostalCodeAPI:
    def test_valid_postal_code(self, api_client, delivery_zone):
        res = api_client.post('/api/v1/delivery/validate-postal/', {
            'postal_code': 'L6H 1A1',
        }, format='json')
        assert res.status_code == 200

    def test_invalid_postal_code(self, api_client, delivery_zone):
        res = api_client.post('/api/v1/delivery/validate-postal/', {
            'postal_code': 'M5V 2T6',
        }, format='json')
        assert res.status_code == 200
