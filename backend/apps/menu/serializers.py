"""
Menu API Serializers.
"""

from rest_framework import serializers
from .models import Category, MenuItem, MenuModifier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name_en', 'name_th', 'slug']


class MenuModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuModifier
        fields = [
            'id', 'name_en', 'name_th', 'price_delta',
            'calories_delta', 'protein_delta_g', 'carbs_delta_g', 'fat_delta_g',
            'is_available'
        ]


class MenuItemListSerializer(serializers.ModelSerializer):
    """Serializer for menu list view with essential fields."""
    category = CategorySerializer(read_only=True)
    macros_summary = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name_en', 'name_th', 'slug', 'category',
            'base_price', 'image_url', 'thumbnail_url',
            'calories', 'protein_g', 'carbs_g', 'fat_g',
            'is_gluten_free', 'is_dairy_free', 'is_halal', 'is_vegetarian',
            'spice_level', 'macros_summary', 'is_featured'
        ]


class MenuItemDetailSerializer(serializers.ModelSerializer):
    """Serializer for single menu item with full details."""
    category = CategorySerializer(read_only=True)
    modifiers = MenuModifierSerializer(many=True, read_only=True)
    macros_summary = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name_en', 'name_th', 'description_en', 'description_th', 'slug',
            'category', 'base_price', 'image_url', 'thumbnail_url',
            # Nutrition
            'calories', 'protein_g', 'carbs_g', 'fat_g', 'fiber_g', 'sodium_mg', 'sugar_g',
            'macros_summary',
            # Allergens & Dietary
            'ingredients_list', 'allergens',
            'is_gluten_free', 'is_dairy_free', 'is_halal', 'is_vegetarian', 'is_vegan',
            'spice_level',
            # Instructions
            'heating_instructions_en', 'heating_instructions_th',
            'storage_instructions', 'shelf_life_days',
            # Modifiers
            'modifiers',
            'is_featured'
        ]
