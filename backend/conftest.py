"""
Shared pytest fixtures for Wela Meal Plan backend.
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model

from apps.accounts.models import CustomerProfile, DeliveryAddress
from apps.menu.models import Category, MenuItem, Ingredient, RecipeComponent
from apps.marketing.models import Coupon
from apps.delivery.models import DeliveryZone, DeliveryWindow

User = get_user_model()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(
        email='admin@welamealprep.ca',
        password='testpass123',
        first_name='Admin',
        last_name='Wela',
    )
    return user


@pytest.fixture
def customer_user(db):
    user = User.objects.create_user(
        email='customer@example.com',
        password='testpass123',
        first_name='John',
        last_name='Doe',
        phone='+19055551234',
    )
    CustomerProfile.objects.create(
        user=user,
        wela_points_balance=500,
    )
    return user


@pytest.fixture
def customer_profile(customer_user):
    return customer_user.profile


@pytest.fixture
def delivery_address(customer_user):
    return DeliveryAddress.objects.create(
        customer=customer_user,
        label='Home',
        recipient_name='John Doe',
        phone='+19055551234',
        street_address='123 Main St',
        city='Oakville',
        province='ON',
        postal_code='L6H 1A1',
        is_default=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name_en='Thai Classics',
        name_th='อาหารไทย',
        slug='thai-classics',
        sort_order=1,
    )


@pytest.fixture
def menu_item(category):
    return MenuItem.objects.create(
        category=category,
        name_en='Pad Thai',
        name_th='ผัดไทย',
        slug='pad-thai',
        base_price=Decimal('14.99'),
        calories=520,
        protein_g=Decimal('28.0'),
        carbs_g=Decimal('62.0'),
        fat_g=Decimal('14.0'),
        fiber_g=Decimal('3.0'),
        sodium_mg=890,
        allergens=['peanuts', 'shellfish', 'eggs'],
        is_gluten_free=True,
        spice_level=1,
        is_active=True,
        is_featured=True,
    )


@pytest.fixture
def menu_item_2(category):
    return MenuItem.objects.create(
        category=category,
        name_en='Green Curry',
        slug='green-curry',
        base_price=Decimal('15.99'),
        calories=480,
        protein_g=Decimal('32.0'),
        carbs_g=Decimal('35.0'),
        fat_g=Decimal('22.0'),
        is_dairy_free=True,
        is_halal=True,
        spice_level=2,
        is_active=True,
    )


@pytest.fixture
def ingredient(db):
    return Ingredient.objects.create(
        name='Jasmine Rice',
        unit='kg',
        current_stock_qty=Decimal('50.00'),
        reorder_threshold=Decimal('10.00'),
        cost_per_unit=Decimal('2.5000'),
        supplier='Thai Rice Co.',
    )


@pytest.fixture
def recipe_component(menu_item, ingredient):
    return RecipeComponent.objects.create(
        menu_item=menu_item,
        ingredient=ingredient,
        quantity=Decimal('0.2000'),
    )


@pytest.fixture
def delivery_zone(db):
    return DeliveryZone.objects.create(
        postal_code_prefix='L6H',
        label='Oakville Central',
        city='Oakville',
        delivery_fee=Decimal('0.00'),
        free_delivery_threshold=Decimal('75.00'),
        is_active=True,
    )


@pytest.fixture
def coupon(db):
    return Coupon.objects.create(
        code='WELCOME15',
        description='15% off first order',
        discount_type='percent',
        discount_value=Decimal('15.00'),
        max_uses=100,
        is_active=True,
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(api_client, customer_user):
    api_client.force_authenticate(user=customer_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
