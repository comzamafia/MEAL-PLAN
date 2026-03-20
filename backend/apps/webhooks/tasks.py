"""
Celery tasks for webhook processing.
"""

from celery import shared_task


@shared_task
def process_stripe_webhook(webhook_event_id: str):
    """Process a Stripe webhook event asynchronously."""
    from apps.webhooks.models import StripeWebhookEvent

    try:
        event = StripeWebhookEvent.objects.get(pk=webhook_event_id)

        if event.status != StripeWebhookEvent.Status.PENDING:
            return  # Already processed

        event.status = StripeWebhookEvent.Status.PROCESSING
        event.save(update_fields=['status'])

        # Route to handler based on event type
        handlers = {
            'payment_intent.succeeded': handle_payment_succeeded,
            'payment_intent.payment_failed': handle_payment_failed,
            'invoice.payment_succeeded': handle_invoice_paid,
            'invoice.payment_failed': handle_invoice_failed,
            'customer.subscription.updated': handle_subscription_updated,
            'customer.subscription.deleted': handle_subscription_deleted,
            'charge.dispute.created': handle_dispute_created,
            'charge.refunded': handle_refund,
        }

        handler = handlers.get(event.event_type)
        if handler:
            handler(event.payload['data']['object'], event)
            event.mark_processed()
        else:
            event.mark_ignored(f"Unhandled event type: {event.event_type}")

    except StripeWebhookEvent.DoesNotExist:
        print(f"[WEBHOOK] Event {webhook_event_id} not found")
    except Exception as e:
        if 'event' in locals():
            event.mark_failed(str(e))
        raise


def handle_payment_succeeded(payment_intent, webhook_event):
    """Handle successful payment - confirm order."""
    from apps.orders.models import Order
    from apps.orders.tasks import send_order_confirmation_email, award_loyalty_points, deduct_ingredient_stock
    from django.utils import timezone

    payment_intent_id = payment_intent['id']

    try:
        order = Order.objects.get(stripe_payment_intent_id=payment_intent_id)
        order.status = Order.Status.CONFIRMED
        order.confirmed_at = timezone.now()
        order.stripe_charge_id = payment_intent.get('latest_charge', '')
        order.save(update_fields=['status', 'confirmed_at', 'stripe_charge_id'])

        webhook_event.related_order_id = order.id
        webhook_event.save(update_fields=['related_order_id'])

        # Trigger follow-up tasks
        send_order_confirmation_email.delay(str(order.id))
        award_loyalty_points.delay(str(order.id))
        deduct_ingredient_stock.delay(str(order.id))

        print(f"[WEBHOOK] Order {order.order_number} confirmed")

    except Order.DoesNotExist:
        print(f"[WEBHOOK] No order found for payment_intent {payment_intent_id}")


def handle_payment_failed(payment_intent, webhook_event):
    """Handle failed payment - mark order as failed."""
    from apps.orders.models import Order

    payment_intent_id = payment_intent['id']

    try:
        order = Order.objects.get(stripe_payment_intent_id=payment_intent_id)
        order.status = Order.Status.FAILED
        order.save(update_fields=['status'])

        webhook_event.related_order_id = order.id
        webhook_event.save(update_fields=['related_order_id'])

        # TODO: Send payment failed email
        print(f"[WEBHOOK] Order {order.order_number} payment failed")

    except Order.DoesNotExist:
        print(f"[WEBHOOK] No order found for payment_intent {payment_intent_id}")


def handle_invoice_paid(invoice, webhook_event):
    """Handle successful subscription invoice - create renewal order."""
    from apps.orders.models import Subscription

    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return

    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)

        # Update last billing date
        subscription.last_billing_date = subscription.next_billing_date
        # Calculate next billing date based on cycle
        from datetime import timedelta
        if subscription.billing_cycle == Subscription.BillingCycle.WEEKLY:
            subscription.next_billing_date += timedelta(days=7)
        elif subscription.billing_cycle == Subscription.BillingCycle.BIWEEKLY:
            subscription.next_billing_date += timedelta(days=14)
        else:  # Monthly
            subscription.next_billing_date += timedelta(days=30)

        subscription.save(update_fields=['last_billing_date', 'next_billing_date'])

        webhook_event.related_subscription_id = subscription.id
        webhook_event.save(update_fields=['related_subscription_id'])

        # TODO: Create renewal order and send confirmation
        print(f"[WEBHOOK] Subscription {subscription.id} renewed")

    except Subscription.DoesNotExist:
        print(f"[WEBHOOK] No subscription found for stripe_subscription {subscription_id}")


def handle_invoice_failed(invoice, webhook_event):
    """Handle failed subscription invoice - set to past_due."""
    from apps.orders.models import Subscription

    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return

    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = Subscription.Status.PAST_DUE
        subscription.save(update_fields=['status'])

        webhook_event.related_subscription_id = subscription.id
        webhook_event.save(update_fields=['related_subscription_id'])

        # TODO: Send payment failed email with retry link
        print(f"[WEBHOOK] Subscription {subscription.id} set to past_due")

    except Subscription.DoesNotExist:
        print(f"[WEBHOOK] No subscription found for stripe_subscription {subscription_id}")


def handle_subscription_updated(stripe_subscription, webhook_event):
    """Sync subscription status from Stripe."""
    from apps.orders.models import Subscription

    subscription_id = stripe_subscription['id']

    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)

        # Map Stripe status to our status
        status_map = {
            'active': Subscription.Status.ACTIVE,
            'past_due': Subscription.Status.PAST_DUE,
            'canceled': Subscription.Status.CANCELLED,
            'paused': Subscription.Status.PAUSED,
            'trialing': Subscription.Status.TRIAL,
        }

        stripe_status = stripe_subscription.get('status')
        if stripe_status in status_map:
            subscription.status = status_map[stripe_status]
            subscription.save(update_fields=['status'])

        webhook_event.related_subscription_id = subscription.id
        webhook_event.save(update_fields=['related_subscription_id'])

        print(f"[WEBHOOK] Subscription {subscription.id} updated to {subscription.status}")

    except Subscription.DoesNotExist:
        print(f"[WEBHOOK] No subscription found for stripe_subscription {subscription_id}")


def handle_subscription_deleted(stripe_subscription, webhook_event):
    """Handle subscription cancellation from Stripe."""
    from apps.orders.models import Subscription
    from django.utils import timezone

    subscription_id = stripe_subscription['id']

    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = Subscription.Status.CANCELLED
        subscription.cancelled_at = timezone.now()
        subscription.save(update_fields=['status', 'cancelled_at'])

        webhook_event.related_subscription_id = subscription.id
        webhook_event.save(update_fields=['related_subscription_id'])

        # TODO: Send cancellation email with win-back offer
        print(f"[WEBHOOK] Subscription {subscription.id} cancelled")

    except Subscription.DoesNotExist:
        print(f"[WEBHOOK] No subscription found for stripe_subscription {subscription_id}")


def handle_dispute_created(dispute, webhook_event):
    """Handle chargeback dispute - alert admin immediately."""
    # TODO: Send urgent alert to admin via Slack/email
    payment_intent = dispute.get('payment_intent')
    amount = dispute.get('amount', 0) / 100  # Convert cents to dollars
    reason = dispute.get('reason', 'unknown')

    print(f"[ALERT] DISPUTE CREATED: Payment {payment_intent}, Amount ${amount}, Reason: {reason}")

    # TODO: Freeze associated order


def handle_refund(charge, webhook_event):
    """Handle refund - update order status and deduct points."""
    from apps.orders.models import Order

    payment_intent = charge.get('payment_intent')

    try:
        order = Order.objects.get(stripe_payment_intent_id=payment_intent)
        order.status = Order.Status.REFUNDED
        order.save(update_fields=['status'])

        webhook_event.related_order_id = order.id
        webhook_event.save(update_fields=['related_order_id'])

        # TODO: Deduct loyalty points earned from this order
        # TODO: Send refund confirmation email
        print(f"[WEBHOOK] Order {order.order_number} refunded")

    except Order.DoesNotExist:
        print(f"[WEBHOOK] No order found for payment_intent {payment_intent}")
