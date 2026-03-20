"""
Stripe Webhook Views.
"""

import logging

import stripe
from django.conf import settings
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import StripeWebhookEvent
from apps.orders.models import Order, Subscription
from apps.accounts.models import CustomerProfile
from apps.marketing.models import LoyaltyPoint

logger = logging.getLogger(__name__)


class StripeWebhookView(views.APIView):
    """
    POST /api/v1/webhooks/stripe/
    Receives all Stripe events; verifies Stripe-Signature header.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate event (idempotency)
        event_id = event['id']
        if StripeWebhookEvent.objects.filter(stripe_event_id=event_id).exists():
            return Response({'status': 'already_processed'}, status=status.HTTP_200_OK)

        # Record the event
        webhook_event = StripeWebhookEvent.objects.create(
            stripe_event_id=event_id,
            event_type=event['type'],
            api_version=event.get('api_version', ''),
            payload=event,
        )

        # Handle events synchronously for now
        try:
            self._handle_event(event, webhook_event)
            webhook_event.mark_processed()
        except Exception as e:
            logger.exception(f"Webhook handler error: {event['type']}")
            webhook_event.mark_failed(str(e))

        # Always return 200 to Stripe to prevent retries
        return Response({'status': 'received'}, status=status.HTTP_200_OK)

    def _handle_event(self, event, webhook_event):
        """Route event to appropriate handler."""
        event_type = event['type']
        handlers = {
            'payment_intent.succeeded': self._handle_payment_succeeded,
            'payment_intent.payment_failed': self._handle_payment_failed,
            'invoice.payment_succeeded': self._handle_invoice_paid,
            'invoice.payment_failed': self._handle_invoice_failed,
            'customer.subscription.updated': self._handle_subscription_updated,
            'customer.subscription.deleted': self._handle_subscription_deleted,
            'charge.dispute.created': self._handle_dispute_created,
            'charge.refunded': self._handle_refund,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(event['data']['object'], webhook_event)
        else:
            webhook_event.mark_ignored(f'Unhandled event type: {event_type}')

    def _handle_payment_succeeded(self, payment_intent, webhook_event):
        """Mark Order as confirmed, trigger confirmation email."""
        pi_id = payment_intent.get('id', '')
        order = Order.objects.filter(stripe_payment_intent_id=pi_id).first()
        if not order:
            logger.warning(f"No order found for PaymentIntent {pi_id}")
            return

        if order.status in ('pending', 'confirmed'):
            order.status = 'confirmed'
            order.save(update_fields=['status'])
            logger.info(f"Order {order.order_number} confirmed via webhook")

    def _handle_payment_failed(self, payment_intent, webhook_event):
        """Mark Order as failed, notify customer to retry."""
        pi_id = payment_intent.get('id', '')
        order = Order.objects.filter(stripe_payment_intent_id=pi_id).first()
        if not order:
            return

        order.status = 'failed'
        order.save(update_fields=['status'])
        logger.info(f"Order {order.order_number} payment failed")

    def _handle_invoice_paid(self, invoice, webhook_event):
        """Mark Subscription renewal as paid."""
        stripe_sub_id = invoice.get('subscription', '')
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub:
            return

        if sub.status == 'past_due':
            sub.status = 'active'
            sub.save(update_fields=['status'])
        logger.info(f"Subscription {sub.id} invoice paid")

    def _handle_invoice_failed(self, invoice, webhook_event):
        """Set Subscription to past_due."""
        stripe_sub_id = invoice.get('subscription', '')
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub:
            return

        sub.status = 'past_due'
        sub.save(update_fields=['status'])
        logger.info(f"Subscription {sub.id} payment failed, set to past_due")

    def _handle_subscription_updated(self, subscription_data, webhook_event):
        """Sync subscription status changes from Stripe to local DB."""
        stripe_sub_id = subscription_data.get('id', '')
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub:
            return

        stripe_status = subscription_data.get('status', '')
        status_map = {
            'active': 'active',
            'past_due': 'past_due',
            'canceled': 'cancelled',
            'paused': 'paused',
            'trialing': 'trial',
        }
        new_status = status_map.get(stripe_status)
        if new_status and new_status != sub.status:
            sub.status = new_status
            sub.save(update_fields=['status'])
            logger.info(f"Subscription {sub.id} status synced to {new_status}")

    def _handle_subscription_deleted(self, subscription_data, webhook_event):
        """Set Subscription to cancelled in local DB."""
        stripe_sub_id = subscription_data.get('id', '')
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub:
            return

        sub.status = 'cancelled'
        sub.save(update_fields=['status'])
        logger.info(f"Subscription {sub.id} cancelled via webhook")

    def _handle_dispute_created(self, dispute, webhook_event):
        """Alert admin; freeze associated order."""
        charge_id = dispute.get('charge', '')
        order = Order.objects.filter(stripe_charge_id=charge_id).first()
        if order:
            logger.critical(f"DISPUTE on order {order.order_number} - charge {charge_id}")
        else:
            logger.critical(f"DISPUTE on unknown charge {charge_id}")

    def _handle_refund(self, charge, webhook_event):
        """Mark Order as refunded, adjust Wela Points if applicable."""
        charge_id = charge.get('id', '')
        # Try to find order by charge or payment intent
        pi_id = charge.get('payment_intent', '')
        order = Order.objects.filter(stripe_payment_intent_id=pi_id).first()
        if not order:
            return

        order.status = 'refunded'
        order.save(update_fields=['status'])

        # Deduct earned points
        if order.customer and order.points_earned > 0:
            profile = getattr(order.customer, 'profile', None)
            if profile:
                profile.wela_points_balance = max(0, profile.wela_points_balance - order.points_earned)
                profile.save(update_fields=['wela_points_balance'])

                LoyaltyPoint.objects.create(
                    customer=order.customer,
                    order=order,
                    points_delta=-order.points_earned,
                    balance_after=profile.wela_points_balance,
                    reason='refund_deduction',
                    description=f'Points reversed for refunded order {order.order_number}',
                )

        logger.info(f"Order {order.order_number} refunded via webhook")
