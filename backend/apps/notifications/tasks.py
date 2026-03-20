"""
Celery tasks for the notifications app.

All email sending is offloaded here so HTTP requests return immediately.
"""

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email(self, order_id):
    """Send order confirmation email asynchronously."""
    try:
        from apps.orders.models import Order
        from apps.notifications.email_service import send_order_confirmation

        order = Order.objects.select_related('customer').prefetch_related('items__menu_item').get(id=order_id)
        send_order_confirmation(order)
    except Exception as exc:
        logger.error(f"[TASK] send_order_confirmation_email failed for {order_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_subscription_confirmation_email(self, subscription_id):
    """Send subscription activation email asynchronously."""
    try:
        from apps.orders.models import Subscription
        from apps.notifications.email_service import send_subscription_confirmation

        subscription = Subscription.objects.select_related('customer').get(id=subscription_id)
        send_subscription_confirmation(subscription)
    except Exception as exc:
        logger.error(f"[TASK] send_subscription_confirmation_email failed for {subscription_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_failed_email(self, order_id, failure_reason=''):
    """Send payment failure notification asynchronously."""
    try:
        from apps.orders.models import Order
        from apps.notifications.email_service import send_payment_failed

        order = Order.objects.select_related('customer').get(id=order_id)
        send_payment_failed(order, failure_reason)
    except Exception as exc:
        logger.error(f"[TASK] send_payment_failed_email failed for {order_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_delivery_dispatched_email(self, order_id):
    """Send delivery dispatched notification asynchronously."""
    try:
        from apps.orders.models import Order
        from apps.notifications.email_service import send_delivery_dispatched

        order = Order.objects.select_related('customer').get(id=order_id)
        send_delivery_dispatched(order)
    except Exception as exc:
        logger.error(f"[TASK] send_delivery_dispatched_email failed for {order_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_referral_reward_email(self, referrer_id, referred_email, points_earned):
    """Send referral reward notification asynchronously."""
    try:
        from django.contrib.auth import get_user_model
        from apps.notifications.email_service import send_referral_reward

        User = get_user_model()
        referrer = User.objects.get(id=referrer_id)
        send_referral_reward(referrer, referred_email, points_earned)
    except Exception as exc:
        logger.error(f"[TASK] send_referral_reward_email failed for {referrer_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, user_id):
    """Send welcome email to new user asynchronously."""
    try:
        from django.contrib.auth import get_user_model
        from apps.notifications.email_service import send_welcome_email

        User = get_user_model()
        user = User.objects.get(id=user_id)
        send_welcome_email(user)
    except Exception as exc:
        logger.error(f"[TASK] send_welcome_email_task failed for {user_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=1, default_retry_delay=300)
def send_low_stock_alert_task(self):
    """Check for low stock ingredients and alert admin."""
    try:
        from apps.menu.models import Ingredient
        from apps.notifications.email_service import send_low_stock_alert

        low_stock = list(Ingredient.objects.filter(
            current_stock_qty__lte=models_F('reorder_threshold')
        ))
        if low_stock:
            send_low_stock_alert(low_stock)
            logger.info(f"[TASK] Low stock alert sent for {len(low_stock)} items")
    except Exception as exc:
        logger.error(f"[TASK] send_low_stock_alert_task failed: {exc}")
        self.retry(exc=exc)


def models_F(field):
    """Helper to import F expression."""
    from django.db.models import F
    return F(field)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def deduct_ingredient_stock(self, order_id):
    """Deduct ingredients from stock after order confirmation."""
    try:
        from django.db.models import F
        from apps.orders.models import Order, OrderItem
        from apps.menu.models import RecipeComponent

        order = Order.objects.get(id=order_id)
        items = OrderItem.objects.filter(order=order).select_related('menu_item')

        for item in items:
            components = RecipeComponent.objects.filter(
                menu_item=item.menu_item
            ).select_related('ingredient')

            for comp in components:
                qty_to_deduct = comp.quantity * item.quantity
                comp.ingredient.current_stock_qty = F('current_stock_qty') - qty_to_deduct
                comp.ingredient.save(update_fields=['current_stock_qty'])

        logger.info(f"[TASK] Stock deducted for order {order.order_number}")
    except Exception as exc:
        logger.error(f"[TASK] deduct_ingredient_stock failed for {order_id}: {exc}")
        self.retry(exc=exc)
