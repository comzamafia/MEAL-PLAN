"""
Delivery API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('zones/', views.DeliveryZoneListView.as_view(), name='delivery-zones'),
    path('validate-postal/', views.ValidatePostalCodeView.as_view(), name='validate-postal'),
    path('route-export/', views.RouteExportView.as_view(), name='route-export'),
]
