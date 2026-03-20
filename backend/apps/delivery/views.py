"""
Delivery API Views.
"""

from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import DeliveryZone, DeliveryWindow
from .serializers import DeliveryZoneSerializer, DeliveryWindowSerializer


class DeliveryZoneListView(generics.ListAPIView):
    """
    GET /api/v1/delivery/zones/
    Returns list of active delivery zones and fees.
    Used for postal code validation at checkout.
    """
    permission_classes = [AllowAny]
    serializer_class = DeliveryZoneSerializer
    queryset = DeliveryZone.objects.filter(is_active=True).order_by('priority', 'label')


class ValidatePostalCodeView(views.APIView):
    """
    POST /api/v1/delivery/validate-postal/
    Validates a postal code against serviceable zones.
    Returns zone, delivery fee, and next available delivery window.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        postal_code = request.data.get('postal_code', '').upper().replace(' ', '')

        if len(postal_code) < 3:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'Invalid postal code format'
            }, status=400)

        # Get first 3 characters (FSA - Forward Sortation Area)
        fsa = postal_code[:3]

        try:
            zone = DeliveryZone.objects.get(postal_code_prefix=fsa, is_active=True)

            # Get next available delivery window
            next_window = DeliveryWindow.objects.filter(
                is_open=True,
            ).filter(
                zones__isnull=True  # Available for all zones, or
            ) | DeliveryWindow.objects.filter(
                zones=zone
            )
            next_window = next_window.first()

            return Response({
                'status': 'success',
                'data': {
                    'serviceable': True,
                    'zone': DeliveryZoneSerializer(zone).data,
                    'delivery_fee': str(zone.delivery_fee),
                    'free_delivery_threshold': str(zone.free_delivery_threshold),
                    'next_delivery_window': DeliveryWindowSerializer(next_window).data if next_window else None
                },
                'message': f'Delivery available to {zone.label}'
            })

        except DeliveryZone.DoesNotExist:
            return Response({
                'status': 'success',
                'data': {
                    'serviceable': False,
                    'zone': None,
                },
                'message': 'Sorry, we do not currently deliver to this area'
            })


class RouteExportView(views.APIView):
    """
    GET /api/v1/delivery/route-export/
    Authenticated admin only; exports delivery order list optimized for routing.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # TODO: Implement route export
        return Response({
            'status': 'success',
            'data': {
                'deliveries': []
            },
            'message': ''
        })
