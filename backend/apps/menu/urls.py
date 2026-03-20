"""
Menu API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.MenuItemListView.as_view(), name='menu-list'),
    path('<uuid:pk>/', views.MenuItemDetailView.as_view(), name='menu-detail'),
]
