"""
Account serializers for user registration, profiles, and addresses.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import CustomerProfile, DeliveryAddress

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
        )
        # Create customer profile
        CustomerProfile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'role', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'created_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for customer profile."""

    user = UserSerializer(read_only=True)
    points_value = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = [
            'user', 'wela_points_balance', 'points_value', 'referral_code',
            'preferred_language', 'email_marketing_opt_in', 'sms_opt_in',
            'dietary_notes', 'created_at'
        ]
        read_only_fields = ['wela_points_balance', 'referral_code', 'created_at']

    def get_points_value(self, obj):
        """Convert points to dollar value (100 points = $1)."""
        return f"{obj.wela_points_balance / 100:.2f}"


class DeliveryAddressSerializer(serializers.ModelSerializer):
    """Serializer for delivery addresses."""

    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = DeliveryAddress
        fields = [
            'id', 'label', 'recipient_name', 'phone',
            'street_address', 'unit', 'city', 'province', 'postal_code',
            'delivery_instructions', 'is_default', 'full_address'
        ]

    def validate_postal_code(self, value):
        """Validate postal code format for Canadian addresses."""
        import re
        # Canadian postal code pattern
        pattern = r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Invalid postal code format. Use format: A1A 1A1"
            )
        return value.upper().replace(' ', '')

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)
