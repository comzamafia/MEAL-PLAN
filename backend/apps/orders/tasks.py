"""
Celery tasks for order processing.
"""

from celery import shared_task
from django.conf import settings
from django.db import models


@shared_task
def send_order_confirmation_email(order_id: str):
    """Send order confirmation email to customer."""
    from apps.orders.models import Order
    from apps.notifications.email_service import send_order_confirmation

    try:
        order = Order.objects.select_related(
            'customer', 'delivery_address'
        ).prefetch_related('items__menu_item').get(pk=order_id)
        send_order_confirmation(order)
    except Order.DoesNotExist:
        print(f"[EMAIL] Order {order_id} not found")


@shared_task
def send_subscription_confirmation_email(subscription_id: str):
    """Send subscription activation email."""
    from apps.orders.models import Subscription
    from apps.notifications.email_service import send_subscription_confirmation

    try:
        subscription = Subscription.objects.select_related('customer').get(pk=subscription_id)
        send_subscription_confirmation(subscription)
    except Subscription.DoesNotExist:
        print(f"[EMAIL] Subscription {subscription_id} not found")


@shared_task
def deduct_ingredient_stock(order_id: str):
    """Deduct ingredient stock based on order items."""
    from apps.orders.models import Order, OrderItem
    from apps.menu.models import RecipeComponent, Ingredient

    try:
        order = Order.objects.prefetch_related('items__menu_item__recipe_components').get(pk=order_id)

        for order_item in order.items.all():
            for component in order_item.menu_item.recipe_components.all():
                quantity_to_deduct = component.quantity * order_item.quantity
                Ingredient.objects.filter(pk=component.ingredient_id).update(
                    current_stock_qty=models.F('current_stock_qty') - quantity_to_deduct
                )

        # Check for low stock alerts
        check_low_stock_alerts.delay()

        print(f"[STOCK] Deducted stock for order {order.order_number}")
    except Order.DoesNotExist:
        print(f"[STOCK] Order {order_id} not found")


@shared_task
def check_low_stock_alerts():
    """Check for ingredients below reorder threshold and send alerts."""
    from apps.menu.models import Ingredient
    from apps.notifications.email_service import send_low_stock_alert

    low_stock_items = list(Ingredient.objects.filter(
        current_stock_qty__lte=models.F('reorder_threshold'),
        is_active=True
    ))

    if low_stock_items:
        send_low_stock_alert(low_stock_items)
        items_list = ', '.join([item.name for item in low_stock_items])
        print(f"[ALERT] Low stock items: {items_list}")


@shared_task
def award_loyalty_points(order_id: str):
    """Award loyalty points for completed order."""
    from apps.orders.models import Order
    from apps.marketing.models import LoyaltyPoint, POINTS_EARN_RATE
    from apps.accounts.models import CustomerProfile

    try:
        order = Order.objects.select_related('customer__profile').get(pk=order_id)

        if order.status != Order.Status.CONFIRMED:
            return

        # Calculate points (10 points per $1 spent)
        points_earned = int(order.subtotal * POINTS_EARN_RATE)

        if points_earned > 0:
            profile = order.customer.profile
            new_balance = profile.wela_points_balance + points_earned

            # Create ledger entry
            LoyaltyPoint.objects.create(
                customer=order.customer,
                points_delta=points_earned,
                balance_after=new_balance,
                reason=LoyaltyPoint.Reason.ORDER_EARNED,
                description=f"Points earned from order {order.order_number}",
                order=order
            )

            # Update balance
            profile.wela_points_balance = new_balance
            profile.save(update_fields=['wela_points_balance'])

            # Update order
            order.points_earned = points_earned
            order.save(update_fields=['points_earned'])

            print(f"[POINTS] Awarded {points_earned} points for order {order.order_number}")

    except Order.DoesNotExist:
        print(f"[POINTS] Order {order_id} not found")


@shared_task
def process_referral_reward(order_id: str):
    """Process referral reward when referred user completes first order."""
    from apps.orders.models import Order
    from apps.marketing.models import ReferralHistory, LoyaltyPoint, REFERRAL_POINTS_REWARD
    from apps.accounts.models import CustomerProfile
    from apps.notifications.email_service import send_referral_reward

    try:
        order = Order.objects.select_related('customer__profile').get(pk=order_id)

        # Check if this is the customer's first order
        customer_orders = Order.objects.filter(
            customer=order.customer,
            status=Order.Status.CONFIRMED
        ).count()

        if customer_orders > 1:
            return  # Not first order

        # Check if customer was referred
        profile = order.customer.profile
        if not profile.referred_by:
            return

        # Find the referral record
        try:
            referral = ReferralHistory.objects.get(
                referred_user=order.customer,
                referrer_reward_issued=False
            )
        except ReferralHistory.DoesNotExist:
            return

        # Award points to referrer
        referrer_profile = referral.referrer.profile
        new_balance = referrer_profile.wela_points_balance + REFERRAL_POINTS_REWARD

        LoyaltyPoint.objects.create(
            customer=referral.referrer,
            points_delta=REFERRAL_POINTS_REWARD,
            balance_after=new_balance,
            reason=LoyaltyPoint.Reason.REFERRAL_BONUS,
            description=f"Referral bonus: {order.customer.email} completed their first order",
            order=order
        )

        referrer_profile.wela_points_balance = new_balance
        referrer_profile.save(update_fields=['wela_points_balance'])

        # Update referral record
        from django.utils import timezone
        referral.referrer_reward_issued = True
        referral.referrer_reward_issued_at = timezone.now()
        referral.referrer_points_earned = REFERRAL_POINTS_REWARD
        referral.qualifying_order = order
        referral.save()

        # Send notification email to referrer
        send_referral_reward(referral.referrer, order.customer.email, REFERRAL_POINTS_REWARD)

        print(f"[REFERRAL] Awarded {REFERRAL_POINTS_REWARD} points to {referral.referrer.email}")

    except Order.DoesNotExist:
        print(f"[REFERRAL] Order {order_id} not found")
