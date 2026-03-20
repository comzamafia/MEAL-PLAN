"""
Subscription Management API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('current/', views.CustomerSubscriptionView.as_view(), name='subscription-current'),
    path('pause/', views.PauseSubscriptionView.as_view(), name='subscription-pause'),
    path('resume/', views.ResumeSubscriptionView.as_view(), name='subscription-resume'),
    path('cancel/', views.CancelSubscriptionView.as_view(), name='subscription-cancel'),
    path('skip-week/', views.SkipWeekView.as_view(), name='subscription-skip-week'),
]
