"""
Checkout and Order API Views.
"""

import json
import uuid
from decimal import Decimal
from datetime import datetime

from django.utils import timezone
from django.db import transaction

from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Order, OrderItem, Subscription
from .serializers import OrderSerializer, SubscriptionSerializer
from apps.menu.models import MenuItem
from apps.marketing.models import Coupon, CouponUsage, LoyaltyPoint
from apps.accounts.models import CustomerProfile


class CreatePaymentIntentView(views.APIView):
    """
    POST /api/v1/checkout/create-intent/
    Creates a Stripe PaymentIntent; returns client_secret.
    For now, calculates the order total server-side and returns a mock client_secret.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        items_data = request.data.get('items', [])
        coupon_code = request.data.get('coupon_code')
        points_to_redeem = int(request.data.get('points_to_redeem', 0))

        if not items_data:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'Cart is empty'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate subtotal from DB prices
        subtotal = Decimal('0.00')
        for item_data in items_data:
            try:
                menu_item = MenuItem.objects.get(id=item_data['menu_item_id'], is_active=True)
                qty = int(item_data.get('quantity', 1))
                subtotal += menu_item.base_price * qty
            except (MenuItem.DoesNotExist, KeyError):
                pass

        # Apply coupon
        discount = Decimal('0.00')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
                if coupon.is_valid:
                    discount = coupon.calculate_discount(subtotal)
            except Coupon.DoesNotExist:
                pass

        # Apply points
        points_value = Decimal(str(points_to_redeem)) / Decimal('100')

        # Calculate delivery fee
        delivery_fee = Decimal('5.99')
        if subtotal >= Decimal('75.00'):
            delivery_fee = Decimal('0.00')

        # HST 13%
        taxable = max(Decimal('0.00'), subtotal - discount - points_value + delivery_fee)
        tax = (taxable * Decimal('0.13')).quantize(Decimal('0.01'))
        total = max(Decimal('0.01'), subtotal - discount - points_value + delivery_fee + tax)

        # In production: stripe.PaymentIntent.create(amount=int(total*100), currency='cad')
        # For now, return a mock client_secret with the calculated total
        mock_secret = f"pi_mock_{uuid.uuid4().hex[:16]}_secret_{uuid.uuid4().hex[:8]}"

        return Response({
            'status': 'success',
            'data': {
                'client_secret': mock_secret,
                'subtotal': str(subtotal),
                'discount': str(discount),
                'delivery_fee': str(delivery_fee),
                'tax': str(tax),
                'total': str(total),
            },
            'message': 'Payment intent created'
        })


class ConfirmOrderView(views.APIView):
    """
    POST /api/v1/checkout/confirm/
    Called after frontend payment confirmation; creates Order and OrderItems in DB.
    """
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id', '')
        items_data = request.data.get('items', [])
        address_data = request.data.get('delivery_address', {})
        coupon_code = request.data.get('coupon_code')
        points_to_redeem = int(request.data.get('points_to_redeem', 0))

        # Generate order number
        today = timezone.now().strftime('%Y%m%d')
        seq = Order.objects.filter(
            created_at__date=timezone.now().date()
        ).count() + 1
        order_number = f"WMP-{today}-{seq:04d}"

        # Calculate totals
        subtotal = Decimal('0.00')
        order_items = []
        for item_data in items_data:
            try:
                menu_item = MenuItem.objects.get(id=item_data.get('menu_item_id'), is_active=True)
                qty = int(item_data.get('quantity', 1))
                item_subtotal = menu_item.base_price * qty
                subtotal += item_subtotal
                order_items.append({
                    'menu_item': menu_item,
                    'quantity': qty,
                    'unit_price': menu_item.base_price,
                    'item_snapshot': {
                        'name_en': menu_item.name_en,
                        'calories': menu_item.calories,
                        'protein_g': float(menu_item.protein_g),
                    },
                })
            except MenuItem.DoesNotExist:
                continue

        discount = Decimal('0.00')
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
                if coupon.is_valid:
                    discount = coupon.calculate_discount(subtotal)
            except Coupon.DoesNotExist:
                pass

        points_value = Decimal(str(points_to_redeem)) / Decimal('100')
        delivery_fee = Decimal('0.00') if subtotal >= Decimal('75.00') else Decimal('5.99')
        taxable = max(Decimal('0.00'), subtotal - discount - points_value + delivery_fee)
        tax = (taxable * Decimal('0.13')).quantize(Decimal('0.01'))
        total = max(Decimal('0.01'), subtotal - discount - points_value + delivery_fee + tax)
        points_earned = int(subtotal * 10)

        # Create order
        order = Order.objects.create(
            order_number=order_number,
            customer=request.user if request.user.is_authenticated else None,
            status='confirmed',
            subtotal=subtotal,
            discount_amount=discount,
            delivery_fee=delivery_fee,
            tax_amount=tax,
            total=total,
            points_earned=points_earned,
            points_redeemed=points_to_redeem,
            points_redemption_value=points_value,
            stripe_payment_intent_id=payment_intent_id,
            delivery_address_snapshot=address_data,
            coupon=coupon,
            confirmed_at=timezone.now(),
        )

        # Create order items
        for oi in order_items:
            OrderItem.objects.create(
                order=order,
                menu_item=oi['menu_item'],
                quantity=oi['quantity'],
                unit_price=oi['unit_price'],
                item_snapshot=oi['item_snapshot'],
            )

        # Record coupon usage
        if coupon:
            CouponUsage.objects.create(
                coupon=coupon,
                customer=request.user if request.user.is_authenticated else None,
                order=order,
                discount_applied=discount,
            )
            coupon.current_uses += 1
            coupon.save(update_fields=['current_uses'])

        # Award loyalty points
        if request.user.is_authenticated:
            profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
            profile.wela_points_balance += points_earned
            profile.save(update_fields=['wela_points_balance'])

            LoyaltyPoint.objects.create(
                customer=request.user,
                order=order,
                points_delta=points_earned,
                balance_after=profile.wela_points_balance,
                reason='order_earned',
                description=f'Earned from order {order_number}',
            )

            # Deduct redeemed points
            if points_to_redeem > 0:
                profile.wela_points_balance -= points_to_redeem
                profile.save(update_fields=['wela_points_balance'])
                LoyaltyPoint.objects.create(
                    customer=request.user,
                    order=order,
                    points_delta=-points_to_redeem,
                    balance_after=profile.wela_points_balance,
                    reason='order_redeemed',
                    description=f'Redeemed on order {order_number}',
                )

        return Response({
            'status': 'success',
            'data': {'order_number': order_number},
            'message': 'Order confirmed'
        })


class OTOUpsellView(views.APIView):
    """
    POST /api/v1/checkout/oto/
    1-click charge using saved Stripe payment method to upgrade order to subscription.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        plan_type = request.data.get('plan_type', 'standard')
        price_map = {
            'starter': Decimal('49.99'),
            'standard': Decimal('89.99'),
            'premium': Decimal('119.99'),
        }
        price = price_map.get(plan_type, Decimal('89.99'))

        sub = Subscription.objects.create(
            customer=request.user,
            plan_type=plan_type,
            billing_cycle='weekly',
            status='active',
            price_per_cycle=price,
            free_delivery=plan_type in ('standard', 'premium'),
        )

        return Response({
            'status': 'success',
            'data': {'subscription_id': str(sub.id), 'plan': plan_type},
            'message': 'Subscription activated'
        })


class OrderBumpView(views.APIView):
    """
    POST /api/v1/checkout/order-bump/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({
            'status': 'success',
            'data': None,
            'message': 'Item added to order'
        })


# Subscription Management Views
class PauseSubscriptionView(views.APIView):
    """
    POST /api/v1/subscriptions/pause/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pause_until = request.data.get('pause_until_date')
        sub = Subscription.objects.filter(
            customer=request.user, status='active'
        ).first()

        if not sub:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)

        sub.status = 'paused'
        sub.pause_until_date = pause_until
        sub.save(update_fields=['status', 'pause_until_date'])

        return Response({
            'status': 'success',
            'data': SubscriptionSerializer(sub).data,
            'message': 'Subscription paused'
        })


class ResumeSubscriptionView(views.APIView):
    """
    POST /api/v1/subscriptions/resume/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sub = Subscription.objects.filter(
            customer=request.user, status='paused'
        ).first()

        if not sub:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'No paused subscription found'
            }, status=status.HTTP_404_NOT_FOUND)

        sub.status = 'active'
        sub.pause_until_date = None
        sub.save(update_fields=['status', 'pause_until_date'])

        return Response({
            'status': 'success',
            'data': SubscriptionSerializer(sub).data,
            'message': 'Subscription resumed'
        })


class CancelSubscriptionView(views.APIView):
    """
    POST /api/v1/subscriptions/cancel/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reason = request.data.get('reason', '')
        sub = Subscription.objects.filter(
            customer=request.user, status__in=['active', 'paused']
        ).first()

        if not sub:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)

        sub.status = 'cancelled'
        sub.cancellation_reason = reason
        sub.save(update_fields=['status', 'cancellation_reason'])

        # In production: cancel Stripe subscription via stripe.Subscription.delete()

        return Response({
            'status': 'success',
            'data': None,
            'message': 'Subscription cancelled'
        })


class SkipWeekView(views.APIView):
    """
    POST /api/v1/subscriptions/skip-week/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        week_date = request.data.get('week_date')
        sub = Subscription.objects.filter(
            customer=request.user, status__in=['active']
        ).first()

        if not sub:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)

        skipped = sub.skipped_weeks or []
        if week_date not in skipped:
            skipped.append(week_date)
            sub.skipped_weeks = skipped
            sub.save(update_fields=['skipped_weeks'])

        return Response({
            'status': 'success',
            'data': SubscriptionSerializer(sub).data,
            'message': f'Week {week_date} skipped'
        })


class CustomerOrderListView(generics.ListAPIView):
    """
    GET /api/v1/orders/my/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user
        ).select_related(
            'delivery_window', 'coupon'
        ).prefetch_related(
            'items__menu_item'
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': ''
        })


class CustomerSubscriptionView(views.APIView):
    """
    GET /api/v1/subscriptions/current/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = Subscription.objects.filter(
            customer=request.user,
            status__in=['active', 'paused', 'past_due', 'trial']
        ).prefetch_related('items__menu_item').first()

        if not subscription:
            return Response({
                'status': 'success',
                'data': None,
                'message': 'No active subscription'
            })

        serializer = SubscriptionSerializer(subscription)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': ''
        })
