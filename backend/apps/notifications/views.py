"""
Notification API Views.
"""

from django.utils import timezone

from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    GET /api/v1/notifications/
    List notifications for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')[:50]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        unread_count = queryset.filter(is_read=False).count()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': {
                'notifications': serializer.data,
                'unread_count': unread_count,
            },
            'message': ''
        })


class NotificationMarkReadView(views.APIView):
    """
    POST /api/v1/notifications/{id}/read/
    Mark a single notification as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk, recipient=request.user
            )
        except Notification.DoesNotExist:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)

        notification.mark_read()
        return Response({
            'status': 'success',
            'data': None,
            'message': 'Marked as read'
        })


class NotificationMarkAllReadView(views.APIView):
    """
    POST /api/v1/notifications/read-all/
    Mark all notifications as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({
            'status': 'success',
            'data': {'marked_count': count},
            'message': f'{count} notifications marked as read'
        })
