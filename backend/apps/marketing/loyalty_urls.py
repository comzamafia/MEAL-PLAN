"""
Loyalty Points API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('balance/', views.LoyaltyBalanceView.as_view(), name='loyalty-balance'),
    path('redeem/', views.RedeemPointsView.as_view(), name='redeem-points'),
]
