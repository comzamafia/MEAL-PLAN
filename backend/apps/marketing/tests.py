"""
Tests for Marketing app — Coupon, LoyaltyPoint, ReferralHistory models and API endpoints.
"""

import pytest
from decimal import Decimal

from django.utils import timezone
from datetime import timedelta

from apps.marketing.models import (
    Coupon, CouponUsage, LoyaltyPoint, ReferralHistory,
    POINTS_TO_DOLLAR_RATE, REFERRAL_DISCOUNT_PERCENT,
)
from apps.accounts.models import CustomerProfile


# ─── Model Tests ────────────────────────────────────────────────────────────

class TestCouponModel:
    def test_str(self, coupon):
        assert 'WELCOME15' in str(coupon)
        assert 'percent' in str(coupon)

    def test_is_valid_active_coupon(self, coupon):
        assert coupon.is_valid is True

    def test_is_valid_inactive(self, coupon):
        coupon.is_active = False
        coupon.save()
        assert coupon.is_valid is False

    def test_is_valid_max_uses_reached(self, coupon):
        coupon.current_uses = coupon.max_uses
        coupon.save()
        assert coupon.is_valid is False

    def test_is_valid_expired(self, coupon):
        coupon.expiry_date = timezone.now() - timedelta(days=1)
        coupon.save()
        assert coupon.is_valid is False

    def test_is_valid_not_started(self, coupon):
        coupon.start_date = timezone.now() + timedelta(days=1)
        coupon.save()
        assert coupon.is_valid is False

    def test_calculate_discount_percent(self, coupon):
        discount = coupon.calculate_discount(Decimal('100.00'))
        assert discount == Decimal('15.00')

    def test_calculate_discount_percent_with_cap(self, coupon):
        coupon.max_discount_amount = Decimal('10.00')
        coupon.save()
        discount = coupon.calculate_discount(Decimal('100.00'))
        assert discount == Decimal('10.00')

    def test_calculate_discount_fixed(self, db):
        c = Coupon.objects.create(
            code='FLAT10',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            is_active=True,
        )
        assert c.calculate_discount(Decimal('50.00')) == Decimal('10.00')

    def test_calculate_discount_fixed_capped_by_subtotal(self, db):
        c = Coupon.objects.create(
            code='FLAT20',
            discount_type='fixed',
            discount_value=Decimal('20.00'),
            is_active=True,
        )
        assert c.calculate_discount(Decimal('15.00')) == Decimal('15.00')

    def test_calculate_discount_free_delivery(self, db):
        c = Coupon.objects.create(
            code='FREEDEL',
            discount_type='free_delivery',
            discount_value=Decimal('0.00'),
            is_active=True,
        )
        assert c.calculate_discount(Decimal('50.00'), delivery_fee=Decimal('5.99')) == Decimal('5.99')


class TestLoyaltyPointModel:
    def test_str_positive(self, customer_user):
        lp = LoyaltyPoint.objects.create(
            customer=customer_user,
            points_delta=100,
            balance_after=600,
            reason='order_earned',
            description='Test earn',
        )
        assert '+100' in str(lp)
        assert 'order_earned' in str(lp)

    def test_str_negative(self, customer_user):
        lp = LoyaltyPoint.objects.create(
            customer=customer_user,
            points_delta=-50,
            balance_after=450,
            reason='order_redeemed',
        )
        assert '-50' in str(lp)


class TestReferralHistoryModel:
    def test_str(self, customer_user, admin_user):
        ref = ReferralHistory.objects.create(
            referrer=customer_user,
            referred_user=admin_user,
        )
        assert customer_user.email in str(ref)
        assert admin_user.email in str(ref)


# ─── API Tests ──────────────────────────────────────────────────────────────

class TestValidateCouponAPI:
    def test_valid_coupon(self, api_client, coupon):
        res = api_client.post('/api/v1/coupons/validate/', {
            'code': 'WELCOME15',
            'subtotal': '100.00',
        }, format='json')
        assert res.status_code == 200
        assert res.data['data']['valid'] is True
        assert Decimal(res.data['data']['discount_amount']) == Decimal('15.00')

    def test_invalid_coupon_code(self, api_client):
        res = api_client.post('/api/v1/coupons/validate/', {
            'code': 'NONEXISTENT',
            'subtotal': '100.00',
        }, format='json')
        assert res.status_code == 200
        assert res.data['data']['valid'] is False

    def test_expired_coupon(self, api_client, coupon):
        coupon.is_active = False
        coupon.save()
        res = api_client.post('/api/v1/coupons/validate/', {
            'code': 'WELCOME15',
            'subtotal': '100.00',
        }, format='json')
        assert res.status_code == 200
        assert res.data['data']['valid'] is False

    def test_min_order_amount_not_met(self, api_client, coupon):
        coupon.min_order_amount = Decimal('50.00')
        coupon.save()
        res = api_client.post('/api/v1/coupons/validate/', {
            'code': 'WELCOME15',
            'subtotal': '25.00',
        }, format='json')
        assert res.status_code == 200
        assert res.data['data']['valid'] is False

    def test_per_customer_usage_limit(self, auth_client, customer_user, coupon):
        from apps.orders.models import Order
        from datetime import date
        order = Order.objects.create(
            customer=customer_user,
            subtotal=Decimal('100.00'),
            total=Decimal('113.00'),
            delivery_date=date.today(),
        )
        CouponUsage.objects.create(
            coupon=coupon,
            customer=customer_user,
            order=order,
            discount_applied=Decimal('15.00'),
        )
        res = auth_client.post('/api/v1/coupons/validate/', {
            'code': 'WELCOME15',
            'subtotal': '100.00',
        }, format='json')
        assert res.status_code == 200
        assert res.data['data']['valid'] is False


class TestLoyaltyBalanceAPI:
    def test_unauthenticated_returns_401(self, api_client):
        res = api_client.get('/api/v1/loyalty/balance/')
        assert res.status_code == 401

    def test_returns_balance(self, auth_client, customer_user):
        res = auth_client.get('/api/v1/loyalty/balance/')
        assert res.status_code == 200
        assert res.data['data']['balance'] == 500  # from fixture


class TestRedeemPointsAPI:
    def test_unauthenticated_returns_401(self, api_client):
        res = api_client.post('/api/v1/loyalty/redeem/', {'points': 100}, format='json')
        assert res.status_code == 401

    def test_redeem_valid_points(self, auth_client, customer_user):
        res = auth_client.post('/api/v1/loyalty/redeem/', {'points': 200}, format='json')
        assert res.status_code == 200
        assert res.data['data']['points_redeemed'] == 200
        assert res.data['data']['remaining_balance'] == 300

    def test_redeem_insufficient_points(self, auth_client, customer_user):
        res = auth_client.post('/api/v1/loyalty/redeem/', {'points': 10000}, format='json')
        assert res.status_code == 400

    def test_redeem_zero_points(self, auth_client):
        res = auth_client.post('/api/v1/loyalty/redeem/', {'points': 0}, format='json')
        assert res.status_code == 400


class TestReferralLinkAPI:
    def test_unauthenticated_returns_401(self, api_client):
        res = api_client.get('/api/v1/referral/link/')
        assert res.status_code == 401

    def test_returns_referral_info(self, auth_client, customer_profile):
        res = auth_client.get('/api/v1/referral/link/')
        assert res.status_code == 200
        assert 'referral_code' in res.data['data']
        assert 'referral_url' in res.data['data']
        assert 'total_referrals' in res.data['data']


class TestApplyReferralAPI:
    def test_invalid_code(self, api_client):
        res = api_client.post('/api/v1/referral/apply/', {'code': 'INVALID'}, format='json')
        assert res.status_code == 400

    def test_valid_code(self, api_client, customer_profile):
        code = customer_profile.referral_code
        res = api_client.post('/api/v1/referral/apply/', {'code': code}, format='json')
        assert res.status_code == 200
        assert res.data['data']['discount_percent'] == REFERRAL_DISCOUNT_PERCENT

    def test_self_referral_blocked(self, auth_client, customer_profile):
        code = customer_profile.referral_code
        res = auth_client.post('/api/v1/referral/apply/', {'code': code}, format='json')
        assert res.status_code == 400

    def test_already_referred_blocked(self, auth_client, customer_user, admin_user):
        admin_profile, _ = CustomerProfile.objects.get_or_create(user=admin_user)
        ReferralHistory.objects.create(
            referrer=admin_user,
            referred_user=customer_user,
        )
        res = auth_client.post('/api/v1/referral/apply/', {
            'code': admin_profile.referral_code,
        }, format='json')
        assert res.status_code == 400
