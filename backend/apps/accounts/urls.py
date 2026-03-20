"""
Account API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('addresses/', views.DeliveryAddressListCreateView.as_view(), name='address-list'),
    path('addresses/<uuid:pk>/', views.DeliveryAddressDetailView.as_view(), name='address-detail'),
    path('addresses/<uuid:pk>/set-default/', views.SetDefaultAddressView.as_view(), name='address-set-default'),
]
