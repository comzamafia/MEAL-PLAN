"""
URL configuration for Wela Meal Plan API.

All API routes are prefixed with /api/v1/
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import health_check

# API v1 URL patterns
api_v1_patterns = [
    # Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('apps.accounts.urls')),

    # App routes
    path('menu/', include('apps.menu.urls')),
    path('checkout/', include('apps.orders.urls')),
    path('subscriptions/', include('apps.orders.subscription_urls')),
    path('coupons/', include('apps.marketing.coupon_urls')),
    path('loyalty/', include('apps.marketing.loyalty_urls')),
    path('referral/', include('apps.marketing.referral_urls')),
    path('delivery/', include('apps.delivery.urls')),
    path('kitchen/', include('apps.menu.kitchen_urls')),
    path('webhooks/', include('apps.webhooks.urls')),
    path('notifications/', include('apps.notifications.urls')),

    # Health check
    path('health/', health_check, name='health_check'),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include((api_v1_patterns, 'api'), namespace='v1')),

    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]

# Swagger UI only in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]

# Django Silk profiler only in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
