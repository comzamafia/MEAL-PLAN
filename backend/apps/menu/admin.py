"""
Admin configuration for menu app.
"""

from django.contrib import admin
from .models import Category, MenuItem, MenuModifier, Ingredient, RecipeComponent


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for menu categories."""

    list_display = ['name_en', 'name_th', 'slug', 'sort_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name_en', 'name_th']
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ['sort_order']


class MenuModifierInline(admin.TabularInline):
    """Inline admin for menu modifiers."""
    model = MenuModifier
    extra = 1


class RecipeComponentInline(admin.TabularInline):
    """Inline admin for recipe components."""
    model = RecipeComponent
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Admin for menu items."""

    list_display = [
        'name_en', 'category', 'base_price', 'calories', 'protein_g',
        'rotation_week', 'is_active', 'is_featured'
    ]
    list_filter = [
        'category', 'is_active', 'is_featured', 'rotation_week',
        'is_gluten_free', 'is_dairy_free', 'is_halal', 'spice_level'
    ]
    search_fields = ['name_en', 'name_th', 'description_en']
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ['sort_order', 'name_en']

    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'name_en', 'name_th', 'description_en', 'description_th', 'slug')
        }),
        ('Pricing & Images', {
            'fields': ('base_price', 'image_url', 'thumbnail_url')
        }),
        ('Nutrition (per serving)', {
            'fields': ('calories', 'protein_g', 'carbs_g', 'fat_g', 'fiber_g', 'sodium_mg', 'sugar_g')
        }),
        ('Dietary & Allergens', {
            'fields': (
                'ingredients_list', 'allergens',
                'is_gluten_free', 'is_dairy_free', 'is_halal', 'is_vegetarian', 'is_vegan',
                'spice_level'
            )
        }),
        ('Instructions', {
            'fields': ('heating_instructions_en', 'heating_instructions_th', 'storage_instructions', 'shelf_life_days')
        }),
        ('Availability', {
            'fields': ('is_active', 'is_featured', 'rotation_week', 'available_from_date', 'available_until_date', 'sort_order')
        }),
    )

    inlines = [MenuModifierInline, RecipeComponentInline]


@admin.register(MenuModifier)
class MenuModifierAdmin(admin.ModelAdmin):
    """Admin for menu modifiers."""

    list_display = ['name_en', 'menu_item', 'price_delta', 'is_available']
    list_filter = ['is_available', 'menu_item__category']
    search_fields = ['name_en', 'menu_item__name_en']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin for raw ingredients."""

    list_display = ['name', 'unit', 'current_stock_qty', 'reorder_threshold', 'cost_per_unit', 'is_low_stock']
    list_filter = ['unit', 'is_active']
    search_fields = ['name', 'supplier']
    ordering = ['name']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


@admin.register(RecipeComponent)
class RecipeComponentAdmin(admin.ModelAdmin):
    """Admin for recipe components."""

    list_display = ['menu_item', 'ingredient', 'quantity', 'cost']
    list_filter = ['menu_item__category']
    search_fields = ['menu_item__name_en', 'ingredient__name']
    autocomplete_fields = ['menu_item', 'ingredient']

    def cost(self, obj):
        return f"${obj.cost:.2f}"
