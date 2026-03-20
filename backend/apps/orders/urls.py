"""
Checkout and Order API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('create-intent/', views.CreatePaymentIntentView.as_view(), name='create-intent'),
    path('confirm/', views.ConfirmOrderView.as_view(), name='confirm-order'),
    path('oto/', views.OTOUpsellView.as_view(), name='oto-upsell'),
    path('order-bump/', views.OrderBumpView.as_view(), name='order-bump'),
    path('my/', views.CustomerOrderListView.as_view(), name='customer-orders'),
]
