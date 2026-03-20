"""
Tests for Menu app - models, serializers, and API endpoints.
"""

import pytest
from decimal import Decimal

from apps.menu.models import Category


@pytest.mark.django_db
class TestCategoryModel:
    def test_str(self, category):
        assert str(category) == 'Thai Classics'

    def test_ordering(self, db):
        Category.objects.create(name_en='B', slug='b', sort_order=2)
        Category.objects.create(name_en='A', slug='a', sort_order=1)
        cats = list(Category.objects.all())
        assert cats[0].name_en == 'A'


@pytest.mark.django_db
class TestMenuItemModel:
    def test_str(self, menu_item):
        assert str(menu_item) == 'Pad Thai'

    def test_macros_summary(self, menu_item):
        assert 'P:28.0g' in menu_item.macros_summary
        assert 'C:62.0g' in menu_item.macros_summary
        assert 'F:14.0g' in menu_item.macros_summary


@pytest.mark.django_db
class TestIngredientModel:
    def test_str(self, ingredient):
        assert 'Jasmine Rice' in str(ingredient)

    def test_is_low_stock(self, ingredient):
        assert not ingredient.is_low_stock
        ingredient.current_stock_qty = Decimal('5.00')
        assert ingredient.is_low_stock


@pytest.mark.django_db
class TestRecipeComponent:
    def test_cost(self, recipe_component):
        assert recipe_component.cost == Decimal('0.5000')


@pytest.mark.django_db
class TestMenuListAPI:
    def test_list_menu_items(self, api_client, menu_item, menu_item_2):
        response = api_client.get('/api/v1/menu/')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert len(data['data']) == 2

    def test_filter_gluten_free(self, api_client, menu_item, menu_item_2):
        response = api_client.get('/api/v1/menu/?is_gluten_free=true')
        assert response.status_code == 200
        items = response.json()['data']
        assert len(items) == 1
        assert items[0]['name_en'] == 'Pad Thai'

    def test_filter_max_calories(self, api_client, menu_item, menu_item_2):
        response = api_client.get('/api/v1/menu/?max_calories=500')
        assert response.status_code == 200
        items = response.json()['data']
        assert len(items) == 1
        assert items[0]['name_en'] == 'Green Curry'

    def test_filter_halal(self, api_client, menu_item, menu_item_2):
        response = api_client.get('/api/v1/menu/?is_halal=true')
        items = response.json()['data']
        assert len(items) == 1
        assert items[0]['name_en'] == 'Green Curry'

    def test_menu_detail(self, api_client, menu_item):
        response = api_client.get(f'/api/v1/menu/{menu_item.id}/')
        assert response.status_code == 200
        data = response.json()['data']
        assert data['name_en'] == 'Pad Thai'
