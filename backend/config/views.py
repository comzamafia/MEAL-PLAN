"""
Health check and utility views.
"""

from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for uptime monitoring.
    Checks database and Redis connectivity.
    """
    health = {
        'status': 'healthy',
        'database': False,
        'cache': False,
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health['database'] = True
    except Exception:
        health['status'] = 'unhealthy'

    # Check Redis cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health['cache'] = True
    except Exception:
        health['status'] = 'unhealthy'

    status_code = 200 if health['status'] == 'healthy' else 503
    return Response(health, status=status_code)
