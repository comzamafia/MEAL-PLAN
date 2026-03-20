"""
Marketing, Loyalty, and Referral API Views.
"""

from decimal import Decimal

from django.db import transaction

from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import (
    Coupon, CouponUsage, LoyaltyPoint, ReferralHistory,
    POINTS_TO_DOLLAR_RATE, REFERRAL_DISCOUNT_PERCENT,
)
from .serializers import LoyaltyPointSerializer
from apps.accounts.models import CustomerProfile


class ValidateCouponView(views.APIView):
    """
    POST /api/v1/coupons/validate/
    Validates coupon code, returns discount amount.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        subtotal = Decimal(str(request.data.get('subtotal', 0)))

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({
                'status': 'success',
                'data': {'valid': False, 'discount_amount': '0.00', 'discount_type': ''},
                'message': 'Coupon not found'
            })

        if not coupon.is_valid:
            return Response({
                'status': 'success',
                'data': {'valid': False, 'discount_amount': '0.00', 'discount_type': ''},
                'message': 'Coupon is expired or has reached its maximum uses'
            })

        if coupon.min_order_amount and subtotal < coupon.min_order_amount:
            return Response({
                'status': 'success',
                'data': {'valid': False, 'discount_amount': '0.00', 'discount_type': ''},
                'message': f'Minimum order amount is ${coupon.min_order_amount}'
            })

        # Check per-customer usage
        if request.user.is_authenticated and coupon.max_uses_per_customer:
            usage_count = CouponUsage.objects.filter(
                coupon=coupon, customer=request.user
            ).count()
            if usage_count >= coupon.max_uses_per_customer:
                return Response({
                    'status': 'success',
                    'data': {'valid': False, 'discount_amount': '0.00', 'discount_type': ''},
                    'message': 'You have already used this coupon'
                })

        discount = coupon.calculate_discount(subtotal)

        return Response({
            'status': 'success',
            'data': {
                'valid': True,
                'discount_amount': str(discount),
                'discount_type': coupon.discount_type,
                'description': coupon.description,
            },
            'message': 'Coupon applied'
        })


class LoyaltyBalanceView(views.APIView):
    """
    GET /api/v1/loyalty/balance/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        transactions = LoyaltyPoint.objects.filter(
            customer=request.user
        ).order_by('-created_at')[:20]

        return Response({
            'status': 'success',
            'data': {
                'balance': profile.wela_points_balance,
                'dollar_value': f"{profile.wela_points_balance / POINTS_TO_DOLLAR_RATE:.2f}",
                'recent_transactions': LoyaltyPointSerializer(transactions, many=True).data
            },
            'message': ''
        })


class RedeemPointsView(views.APIView):
    """
    POST /api/v1/loyalty/redeem/
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        points = int(request.data.get('points', 0))
        if points <= 0:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'Points must be greater than 0'
            }, status=400)

        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

        if points > profile.wela_points_balance:
            return Response({
                'status': 'error',
                'data': None,
                'message': f'Insufficient points. You have {profile.wela_points_balance} points.'
            }, status=400)

        dollar_value = Decimal(str(points)) / POINTS_TO_DOLLAR_RATE
        profile.wela_points_balance -= points
        profile.save(update_fields=['wela_points_balance'])

        LoyaltyPoint.objects.create(
            customer=request.user,
            points_delta=-points,
            balance_after=profile.wela_points_balance,
            reason='order_redeemed',
            description=f'Redeemed {points} points (${dollar_value:.2f})',
        )

        return Response({
            'status': 'success',
            'data': {
                'points_redeemed': points,
                'discount_applied': str(dollar_value),
                'remaining_balance': profile.wela_points_balance,
            },
            'message': 'Points redeemed'
        })


class ReferralLinkView(views.APIView):
    """
    GET /api/v1/referral/link/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        referrals = ReferralHistory.objects.filter(referrer=request.user)
        total_referrals = referrals.count()
        pending_rewards = referrals.filter(referrer_reward_issued=False).count()
        earned_points = sum(r.referrer_points_earned for r in referrals if r.referrer_reward_issued)

        return Response({
            'status': 'success',
            'data': {
                'referral_code': profile.referral_code,
                'referral_url': f"https://welamealprep.ca/?ref={profile.referral_code}",
                'total_referrals': total_referrals,
                'pending_rewards': pending_rewards,
                'earned_points': earned_points,
            },
            'message': ''
        })


class ApplyReferralView(views.APIView):
    """
    POST /api/v1/referral/apply/
    Validates and applies a referral code during checkout.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()

        try:
            referrer_profile = CustomerProfile.objects.get(referral_code=code)
        except CustomerProfile.DoesNotExist:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'Invalid referral code'
            }, status=400)

        # Don't let users apply their own code
        if request.user.is_authenticated and request.user == referrer_profile.user:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'You cannot use your own referral code'
            }, status=400)

        # Check if already referred
        if request.user.is_authenticated:
            if ReferralHistory.objects.filter(referred_user=request.user).exists():
                return Response({
                    'status': 'error',
                    'data': None,
                    'message': 'You have already used a referral code'
                }, status=400)

        return Response({
            'status': 'success',
            'data': {
                'discount_percent': REFERRAL_DISCOUNT_PERCENT,
                'referrer_name': referrer_profile.user.first_name,
            },
            'message': f'{REFERRAL_DISCOUNT_PERCENT}% discount will be applied to your order'
        })
