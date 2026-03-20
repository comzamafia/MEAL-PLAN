"""
Referral API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('link/', views.ReferralLinkView.as_view(), name='referral-link'),
    path('apply/', views.ApplyReferralView.as_view(), name='apply-referral'),
]
