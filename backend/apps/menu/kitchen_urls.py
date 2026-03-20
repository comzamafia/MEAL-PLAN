"""
Kitchen Operations API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('prep-list/', views.PrepListView.as_view(), name='prep-list'),
    path('procurement/', views.ProcurementView.as_view(), name='procurement'),
    path('recipe-matrix/', views.RecipeMatrixView.as_view(), name='recipe-matrix'),
]
