"""
Email service for sending transactional emails via Postmark.
"""

import logging
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Postmark API."""

    # Template aliases (configure these in Postmark)
    TEMPLATES = {
        'order_confirmation': 'order-confirmation',
        'subscription_activated': 'subscription-activated',
        'subscription_paused': 'subscription-paused',
        'subscription_cancelled': 'subscription-cancelled',
        'payment_reminder': 'payment-reminder',
        'payment_failed': 'payment-failed',
        'delivery_dispatched': 'delivery-dispatched',
        'delivery_completed': 'delivery-completed',
        'referral_reward': 'referral-reward',
        'welcome': 'welcome',
        'password_reset': 'password-reset',
        'low_stock_alert': 'low-stock-alert',
    }

    def __init__(self):
        self.api_token = getattr(settings, 'POSTMARK_API_TOKEN', None)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'hello@welamealprep.ca')
        self.enabled = bool(self.api_token) and getattr(settings, 'EMAIL_ENABLED', True)

    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> bool:
        """Send a basic email."""
        if not self.enabled:
            logger.info(f"[EMAIL-DISABLED] Would send to {to}: {subject}")
            return True

        try:
            import requests

            response = requests.post(
                'https://api.postmarkapp.com/email',
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Postmark-Server-Token': self.api_token,
                },
                json={
                    'From': self.from_email,
                    'To': to,
                    'Subject': subject,
                    'HtmlBody': html_body,
                    'TextBody': text_body or '',
                    'Tag': tag,
                    'MessageStream': 'outbound',
                },
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"[EMAIL] Sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"[EMAIL-ERROR] Failed to send to {to}: {e}")
            return False

    def send_template_email(
        self,
        to: str,
        template_alias: str,
        template_model: Dict,
        tag: Optional[str] = None,
    ) -> bool:
        """Send an email using a Postmark template."""
        if not self.enabled:
            logger.info(f"[EMAIL-DISABLED] Would send template {template_alias} to {to}")
            return True

        try:
            import requests

            response = requests.post(
                'https://api.postmarkapp.com/email/withTemplate',
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Postmark-Server-Token': self.api_token,
                },
                json={
                    'From': self.from_email,
                    'To': to,
                    'TemplateAlias': template_alias,
                    'TemplateModel': template_model,
                    'Tag': tag,
                    'MessageStream': 'outbound',
                },
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"[EMAIL] Sent template {template_alias} to {to}")
            return True

        except Exception as e:
            logger.error(f"[EMAIL-ERROR] Failed to send template {template_alias} to {to}: {e}")
            return False


# Singleton instance
email_service = EmailService()


def send_order_confirmation(order) -> bool:
    """Send order confirmation email."""
    template_model = {
        'customer_name': order.customer.first_name or order.customer.email,
        'order_number': order.order_number,
        'order_date': order.created_at.strftime('%B %d, %Y'),
        'delivery_date': order.delivery_date.strftime('%A, %B %d, %Y') if order.delivery_date else 'TBD',
        'delivery_address': str(order.delivery_address) if order.delivery_address else '',
        'items': [
            {
                'name': item.menu_item_name,
                'quantity': item.quantity,
                'price': f"${item.unit_price:.2f}",
                'total': f"${item.total_price:.2f}",
            }
            for item in order.items.all()
        ],
        'subtotal': f"${order.subtotal:.2f}",
        'tax': f"${order.tax_amount:.2f}",
        'total': f"${order.total:.2f}",
        'points_earned': order.points_earned or 0,
    }

    return email_service.send_template_email(
        to=order.customer.email,
        template_alias=EmailService.TEMPLATES['order_confirmation'],
        template_model=template_model,
        tag='order-confirmation',
    )


def send_subscription_confirmation(subscription) -> bool:
    """Send subscription activation email."""
    from apps.orders.models import SubscriptionItem

    items = SubscriptionItem.objects.filter(subscription=subscription).select_related('menu_item')

    template_model = {
        'customer_name': subscription.customer.first_name or subscription.customer.email,
        'frequency': subscription.get_frequency_display(),
        'next_delivery': subscription.next_delivery_date.strftime('%A, %B %d, %Y') if subscription.next_delivery_date else 'TBD',
        'items': [
            {
                'name': item.menu_item.name,
                'quantity': item.quantity,
            }
            for item in items
        ],
    }

    return email_service.send_template_email(
        to=subscription.customer.email,
        template_alias=EmailService.TEMPLATES['subscription_activated'],
        template_model=template_model,
        tag='subscription-activated',
    )


def send_payment_failed(order, failure_reason: str = '') -> bool:
    """Send payment failure notification."""
    template_model = {
        'customer_name': order.customer.first_name or order.customer.email,
        'order_number': order.order_number,
        'amount': f"${order.total:.2f}",
        'failure_reason': failure_reason,
        'retry_url': f"{settings.FRONTEND_URL}/dashboard/orders/{order.id}",
    }

    return email_service.send_template_email(
        to=order.customer.email,
        template_alias=EmailService.TEMPLATES['payment_failed'],
        template_model=template_model,
        tag='payment-failed',
    )


def send_delivery_dispatched(order) -> bool:
    """Send delivery notification."""
    template_model = {
        'customer_name': order.customer.first_name or order.customer.email,
        'order_number': order.order_number,
        'delivery_window': '3:00 PM - 5:00 PM',
        'delivery_address': str(order.delivery_address) if order.delivery_address else '',
    }

    return email_service.send_template_email(
        to=order.customer.email,
        template_alias=EmailService.TEMPLATES['delivery_dispatched'],
        template_model=template_model,
        tag='delivery-dispatched',
    )


def send_referral_reward(referrer, referred_email: str, points_earned: int) -> bool:
    """Send referral reward notification."""
    template_model = {
        'customer_name': referrer.first_name or referrer.email,
        'referred_email': referred_email,
        'points_earned': points_earned,
        'points_value': f"${points_earned / 100:.2f}",  # 100 points = $1
    }

    return email_service.send_template_email(
        to=referrer.email,
        template_alias=EmailService.TEMPLATES['referral_reward'],
        template_model=template_model,
        tag='referral-reward',
    )


def send_welcome_email(user) -> bool:
    """Send welcome email to new user."""
    template_model = {
        'customer_name': user.first_name or user.email,
        'login_url': f"{settings.FRONTEND_URL}/login",
    }

    return email_service.send_template_email(
        to=user.email,
        template_alias=EmailService.TEMPLATES['welcome'],
        template_model=template_model,
        tag='welcome',
    )


def send_low_stock_alert(low_stock_items: List) -> bool:
    """Send low stock alert to admin."""
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@welamealprep.ca')

    template_model = {
        'items': [
            {
                'name': item.name,
                'current_stock': item.current_stock_qty,
                'reorder_threshold': item.reorder_threshold,
                'unit': item.unit,
            }
            for item in low_stock_items
        ],
        'item_count': len(low_stock_items),
    }

    return email_service.send_template_email(
        to=admin_email,
        template_alias=EmailService.TEMPLATES['low_stock_alert'],
        template_model=template_model,
        tag='low-stock-alert',
    )
