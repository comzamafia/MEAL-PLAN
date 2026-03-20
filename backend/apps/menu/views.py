"""
Menu API Views.
"""

import csv
from decimal import Decimal

from django.http import HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone

from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import MenuItem, RecipeComponent
from .serializers import MenuItemListSerializer, MenuItemDetailSerializer
from apps.orders.models import Order, OrderItem


class MenuItemListView(generics.ListAPIView):
    """
    GET /api/v1/menu/
    Returns menu items for the current rotation week with macros.
    Cached for 5 minutes to reduce DB load.
    """
    permission_classes = [AllowAny]
    serializer_class = MenuItemListSerializer
    ordering = ['sort_order']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='category', description='Filter by category ID', type=str),
            OpenApiParameter(name='is_gluten_free', description='Filter gluten-free items', type=bool),
            OpenApiParameter(name='is_dairy_free', description='Filter dairy-free items', type=bool),
            OpenApiParameter(name='is_halal', description='Filter halal items', type=bool),
            OpenApiParameter(name='max_calories', description='Maximum calories per serving', type=int),
            OpenApiParameter(name='min_protein', description='Minimum protein (g) per serving', type=float),
            OpenApiParameter(name='allergen_exclude', description='Comma-separated allergens to exclude', type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = MenuItem.objects.filter(is_active=True).select_related('category')

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        for field in ['is_gluten_free', 'is_dairy_free', 'is_halal', 'is_vegetarian', 'is_vegan']:
            value = self.request.query_params.get(field)
            if value and value.lower() == 'true':
                queryset = queryset.filter(**{field: True})

        rotation_week = self.request.query_params.get('rotation_week')
        if rotation_week:
            queryset = queryset.filter(rotation_week=int(rotation_week))

        max_calories = self.request.query_params.get('max_calories')
        if max_calories:
            queryset = queryset.filter(calories__lte=int(max_calories))

        min_protein = self.request.query_params.get('min_protein')
        if min_protein:
            queryset = queryset.filter(protein_g__gte=float(min_protein))

        allergen_exclude = self.request.query_params.get('allergen_exclude')
        if allergen_exclude:
            allergens_to_exclude = allergen_exclude.split(',')
            for allergen in allergens_to_exclude:
                queryset = queryset.exclude(allergens__contains=[allergen.strip()])

        return queryset


class MenuItemDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/menu/{id}/
    Cached for 5 minutes.
    """
    permission_classes = [AllowAny]
    serializer_class = MenuItemDetailSerializer
    queryset = MenuItem.objects.filter(is_active=True).select_related('category').prefetch_related('modifiers')


# Kitchen Operations Views (staff only)
class PrepListView(views.APIView):
    """
    GET /api/v1/kitchen/prep-list/?date=YYYY-MM-DD&format=json|csv
    Aggregated quantities per menu item for a delivery date.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_str = request.query_params.get('date')
        output_format = request.query_params.get('format', 'json')

        filters = Q(status__in=['confirmed', 'prep'])
        if date_str:
            filters &= Q(delivery_window__date=date_str)
        else:
            filters &= Q(delivery_window__date=timezone.now().date())

        prep_items = OrderItem.objects.filter(
            order__in=Order.objects.filter(filters)
        ).values(
            'menu_item__name_en',
            'menu_item__id',
        ).annotate(
            total_qty=Sum('quantity'),
        ).order_by('menu_item__name_en')

        prep_list = [
            {
                'menu_item_id': str(item['menu_item__id']),
                'name': item['menu_item__name_en'],
                'total_quantity': item['total_qty'],
            }
            for item in prep_items
        ]

        if output_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="prep-list-{date_str or "today"}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Menu Item', 'Total Quantity'])
            for item in prep_list:
                writer.writerow([item['name'], item['total_quantity']])
            return response

        return Response({
            'status': 'success',
            'data': prep_list,
            'message': ''
        })


class ProcurementView(views.APIView):
    """
    GET /api/v1/kitchen/procurement/?date=YYYY-MM-DD&format=json|csv
    Raw ingredient purchase summary after cut-off.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_str = request.query_params.get('date')
        output_format = request.query_params.get('format', 'json')

        filters = Q(status__in=['confirmed', 'prep'])
        if date_str:
            filters &= Q(delivery_window__date=date_str)

        order_items = OrderItem.objects.filter(
            order__in=Order.objects.filter(filters)
        ).values('menu_item_id').annotate(total_qty=Sum('quantity'))

        ingredient_needs: dict[str, dict] = {}
        for oi in order_items:
            components = RecipeComponent.objects.filter(
                menu_item_id=oi['menu_item_id']
            ).select_related('ingredient')

            for comp in components:
                ing = comp.ingredient
                key = str(ing.id)
                needed = float(comp.quantity) * oi['total_qty']

                if key not in ingredient_needs:
                    ingredient_needs[key] = {
                        'ingredient_id': key,
                        'name': ing.name,
                        'unit': ing.unit,
                        'total_needed': 0.0,
                        'current_stock': float(ing.current_stock_qty),
                        'cost_per_unit': float(ing.cost_per_unit),
                        'supplier': ing.supplier,
                    }
                ingredient_needs[key]['total_needed'] += needed

        procurement = []
        for data in ingredient_needs.values():
            shortfall = max(0.0, data['total_needed'] - data['current_stock'])
            data['shortfall'] = shortfall
            data['estimated_cost'] = round(shortfall * data['cost_per_unit'], 2)
            procurement.append(data)
        procurement.sort(key=lambda x: x['name'])

        if output_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="procurement-{date_str or "all"}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Ingredient', 'Unit', 'Needed', 'In Stock', 'To Order', 'Cost/Unit', 'Est. Cost', 'Supplier'])
            for item in procurement:
                writer.writerow([
                    item['name'], item['unit'],
                    f"{item['total_needed']:.2f}", f"{item['current_stock']:.2f}",
                    f"{item['shortfall']:.2f}", f"{item['cost_per_unit']:.4f}",
                    f"{item['estimated_cost']:.2f}", item['supplier'],
                ])
            return response

        return Response({
            'status': 'success',
            'data': procurement,
            'message': ''
        })


class RecipeMatrixView(views.APIView):
    """
    GET /api/v1/kitchen/recipe-matrix/?format=json|csv
    Full Standard Recipe Matrix with ingredient proportions and food cost.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        output_format = request.query_params.get('format', 'json')

        menu_items = MenuItem.objects.filter(
            is_active=True
        ).prefetch_related('recipe_components__ingredient').order_by('name_en')

        matrix = []
        for item in menu_items:
            components = []
            total_cost = Decimal('0.00')
            for comp in item.recipe_components.all():
                cost = comp.cost
                total_cost += cost
                components.append({
                    'ingredient': comp.ingredient.name,
                    'quantity': float(comp.quantity),
                    'unit': comp.ingredient.unit,
                    'cost': float(cost),
                })

            margin = float(
                ((item.base_price - total_cost) / item.base_price * 100)
                if item.base_price > 0 else 0
            )
            matrix.append({
                'menu_item': item.name_en,
                'base_price': float(item.base_price),
                'food_cost': float(total_cost),
                'margin_pct': margin,
                'components': components,
            })

        if output_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="recipe-matrix.csv"'
            writer = csv.writer(response)
            writer.writerow(['Menu Item', 'Ingredient', 'Qty', 'Unit', 'Cost', 'Base Price', 'Food Cost', 'Margin %'])
            for item in matrix:
                for comp in item['components']:
                    writer.writerow([
                        item['menu_item'], comp['ingredient'],
                        f"{comp['quantity']:.4f}", comp['unit'],
                        f"{comp['cost']:.4f}", f"{item['base_price']:.2f}",
                        f"{item['food_cost']:.2f}", f"{item['margin_pct']:.1f}",
                    ])
            return response

        return Response({
            'status': 'success',
            'data': matrix,
            'message': ''
        })
