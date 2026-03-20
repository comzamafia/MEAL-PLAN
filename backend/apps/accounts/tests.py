"""
Tests for Accounts app - models and API endpoints.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self, customer_user):
        assert customer_user.email == 'customer@example.com'
        assert customer_user.role == 'customer'
        assert customer_user.check_password('testpass123')

    def test_create_superuser(self, admin_user):
        assert admin_user.is_superuser
        assert admin_user.is_staff
        assert admin_user.role == 'admin'


@pytest.mark.django_db
class TestCustomerProfile:
    def test_auto_referral_code(self, customer_profile):
        assert len(customer_profile.referral_code) == 8
        assert customer_profile.referral_code.isalnum()

    def test_wela_points(self, customer_profile):
        assert customer_profile.wela_points_balance == 500


@pytest.mark.django_db
class TestDeliveryAddressModel:
    def test_full_address(self, delivery_address):
        assert 'Oakville' in delivery_address.full_address
        assert 'L6H 1A1' in delivery_address.full_address


@pytest.mark.django_db
class TestProfileAPI:
    def test_get_profile(self, auth_client):
        response = auth_client.get('/api/v1/auth/profile/')
        assert response.status_code == 200
        data = response.json()['data']
        assert data['user']['email'] == 'customer@example.com'
        assert data['wela_points_balance'] == 500

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/auth/profile/')
        assert response.status_code == 401


@pytest.mark.django_db
class TestAddressAPI:
    def test_create_address(self, auth_client):
        response = auth_client.post('/api/v1/auth/addresses/', {
            'label': 'Work',
            'recipient_name': 'John Doe',
            'phone': '+19055551234',
            'street_address': '456 Oak Ave',
            'city': 'Burlington',
            'province': 'ON',
            'postal_code': 'L7L 1A1',
        }, format='json')
        assert response.status_code in (200, 201)

    def test_list_addresses(self, auth_client, delivery_address):
        response = auth_client.get('/api/v1/auth/addresses/')
        assert response.status_code == 200
