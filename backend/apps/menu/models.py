"""
Menu and Product models for Wela Meal Plan.

Includes:
- Category: Main menu categories
- MenuItem: Full menu item with nutrition and allergen data
- MenuModifier: Add-on options (rice swap, extra egg, etc.)
- Ingredient: Raw ingredients for inventory
- RecipeComponent: Links MenuItem to ingredients for food cost
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """
    Menu categories (The Perfect Box, The Lean Grill, Bulk Protein, etc.)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_en = models.CharField(max_length=100)
    name_th = models.CharField(max_length=100, blank=True)
    description_en = models.TextField(blank=True)
    description_th = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_categories'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name_en']

    def __str__(self):
        return self.name_en


class MenuItem(models.Model):
    """
    Full menu item with nutrition, allergens, and availability.
    """

    class SpiceLevel(models.IntegerChoices):
        NONE = 0, 'Not Spicy'
        MILD = 1, 'Mild'
        MEDIUM = 2, 'Medium'
        HOT = 3, 'Hot'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='items'
    )

    # Basic Info
    name_en = models.CharField(max_length=200)
    name_th = models.CharField(max_length=200, blank=True)
    description_en = models.TextField(blank=True)
    description_th = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    # Pricing
    base_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Images (S3/CDN paths)
    image_url = models.URLField(max_length=500, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)

    # Nutrition (per box/serving)
    calories = models.PositiveIntegerField(default=0, help_text="kcal per serving")
    protein_g = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    carbs_g = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    fat_g = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    fiber_g = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    sodium_mg = models.PositiveIntegerField(default=0)
    sugar_g = models.DecimalField(max_digits=6, decimal_places=1, default=0)

    # Allergens & Dietary (JSON array for allergens)
    ingredients_list = models.TextField(blank=True, help_text="Full ingredient list")
    allergens = models.JSONField(default=list, blank=True, help_text="['peanuts', 'shellfish', etc.]")
    is_gluten_free = models.BooleanField(default=False)
    is_dairy_free = models.BooleanField(default=False)
    is_halal = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    spice_level = models.PositiveSmallIntegerField(
        choices=SpiceLevel.choices,
        default=SpiceLevel.NONE
    )

    # Consumption Instructions
    heating_instructions_en = models.TextField(blank=True)
    heating_instructions_th = models.TextField(blank=True)
    storage_instructions = models.TextField(blank=True, default="Keep refrigerated at 4°C or below")
    shelf_life_days = models.PositiveSmallIntegerField(default=5)

    # Availability Management
    is_active = models.BooleanField(default=True, db_index=True)
    rotation_week = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Menu rotation week (1-4)"
    )
    available_from_date = models.DateField(null=True, blank=True)
    available_until_date = models.DateField(null=True, blank=True)

    # Sort and popularity
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_items'
        ordering = ['sort_order', 'name_en']
        indexes = [
            models.Index(fields=['is_active', 'rotation_week']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name_en

    @property
    def macros_summary(self):
        """Return formatted macros string."""
        return f"P:{self.protein_g}g C:{self.carbs_g}g F:{self.fat_g}g"


class MenuModifier(models.Model):
    """
    Add-on options for menu items (rice swap, boiled egg, etc.)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='modifiers'
    )

    name_en = models.CharField(max_length=100)
    name_th = models.CharField(max_length=100, blank=True)
    price_delta = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Price change (+/-)"
    )

    # Nutrition impact
    calories_delta = models.IntegerField(default=0)
    protein_delta_g = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    carbs_delta_g = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    fat_delta_g = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    is_available = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_modifiers'
        ordering = ['sort_order', 'name_en']

    def __str__(self):
        sign = '+' if self.price_delta >= 0 else ''
        return f"{self.name_en} ({sign}${self.price_delta})"


class Ingredient(models.Model):
    """
    Raw ingredient master for inventory and food cost tracking.
    """

    class Unit(models.TextChoices):
        KG = 'kg', 'Kilograms'
        G = 'g', 'Grams'
        L = 'l', 'Liters'
        ML = 'ml', 'Milliliters'
        UNIT = 'unit', 'Units/Pieces'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.G)

    # Inventory
    current_stock_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Costing
    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    supplier = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ingredients'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def is_low_stock(self):
        return self.current_stock_qty <= self.reorder_threshold


class RecipeComponent(models.Model):
    """
    Links MenuItem to Ingredients for food cost calculation
    and automatic stock deduction.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='recipe_components'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='used_in'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))]
    )

    class Meta:
        db_table = 'recipe_components'
        unique_together = ['menu_item', 'ingredient']

    def __str__(self):
        return f"{self.ingredient.name} in {self.menu_item.name_en}"

    @property
    def cost(self):
        return self.quantity * self.ingredient.cost_per_unit
