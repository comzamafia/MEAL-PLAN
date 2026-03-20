"""
Account API Views for user management.
"""

from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import CustomerProfile, DeliveryAddress
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CustomerProfileSerializer,
    DeliveryAddressSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Register a new customer account.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'status': 'success',
            'data': UserSerializer(user).data,
            'message': 'Account created successfully. Please log in.'
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/v1/auth/profile/
    Get or update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    def get_object(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': ''
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': 'Profile updated successfully.'
        })


class DeliveryAddressListCreateView(generics.ListCreateAPIView):
    """
    GET/POST /api/v1/auth/addresses/
    List or create delivery addresses for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryAddressSerializer

    def get_queryset(self):
        return DeliveryAddress.objects.filter(customer=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': ''
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': 'Address added successfully.'
        }, status=status.HTTP_201_CREATED)


class DeliveryAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/v1/auth/addresses/{id}/
    Manage a specific delivery address.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryAddressSerializer

    def get_queryset(self):
        return DeliveryAddress.objects.filter(customer=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': ''
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': 'Address updated successfully.'
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'data': None,
            'message': 'Address deleted successfully.'
        }, status=status.HTTP_200_OK)


class SetDefaultAddressView(views.APIView):
    """
    POST /api/v1/auth/addresses/{id}/set-default/
    Set an address as the default delivery address.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            address = DeliveryAddress.objects.get(pk=pk, customer=request.user)
            address.is_default = True
            address.save()
            return Response({
                'status': 'success',
                'data': DeliveryAddressSerializer(address).data,
                'message': 'Default address updated.'
            })
        except DeliveryAddress.DoesNotExist:
            return Response({
                'status': 'error',
                'data': None,
                'message': 'Address not found.'
            }, status=status.HTTP_404_NOT_FOUND)
