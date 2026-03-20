"""
Generate procurement summary for ingredient ordering.

Usage:
    python manage.py procurement_summary --date 2026-03-22
    python manage.py procurement_summary --next-sunday
"""

import csv
from datetime import date, timedelta
from io import StringIO

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, F

from apps.orders.models import Order, OrderItem
from apps.menu.models import RecipeComponent, Ingredient


class Command(BaseCommand):
    help = 'Generate procurement summary showing what ingredients to order'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Delivery date in YYYY-MM-DD format'
        )
        parser.add_argument(
            '--next-sunday',
            action='store_true',
            help='Generate for next Sunday'
        )
        parser.add_argument(
            '--format',
            choices=['text', 'csv'],
            default='text',
            help='Output format'
        )

    def handle(self, *args, **options):
        # Determine delivery date
        if options['next_sunday']:
            today = date.today()
            days_until_sunday = (6 - today.weekday()) % 7
            if days_until_sunday == 0:
                days_until_sunday = 7
            delivery_date = today + timedelta(days=days_until_sunday)
        elif options['date']:
            try:
                delivery_date = date.fromisoformat(options['date'])
            except ValueError:
                raise CommandError('Invalid date format. Use YYYY-MM-DD')
        else:
            raise CommandError('Specify --date or --next-sunday')

        # Get orders for the delivery date
        orders = Order.objects.filter(
            delivery_date=delivery_date,
            status__in=[Order.Status.PENDING, Order.Status.CONFIRMED]
        ).prefetch_related('items__menu_item')

        if not orders.exists():
            self.stdout.write(
                self.style.WARNING(f'No orders found for {delivery_date}')
            )
            return

        # Calculate required ingredients
        ingredient_requirements = {}

        for order in orders:
            for item in order.items.all():
                if not item.menu_item_id:
                    continue

                components = RecipeComponent.objects.filter(
                    menu_item_id=item.menu_item_id
                ).select_related('ingredient')

                for component in components:
                    ing_id = component.ingredient_id
                    if ing_id not in ingredient_requirements:
                        ingredient_requirements[ing_id] = {
                            'ingredient': component.ingredient,
                            'required': 0,
                            'cost': 0
                        }
                    qty_needed = component.quantity * item.quantity
                    ingredient_requirements[ing_id]['required'] += qty_needed
                    ingredient_requirements[ing_id]['cost'] += component.cost * item.quantity

        # Compare with current stock
        procurement_list = []

        for ing_id, data in ingredient_requirements.items():
            ing = data['ingredient']
            required = data['required']
            current_stock = ing.current_stock_qty
            shortfall = max(0, required - current_stock)

            procurement_list.append({
                'name': ing.name,
                'unit': ing.unit,
                'required': required,
                'in_stock': current_stock,
                'to_order': shortfall,
                'supplier': ing.supplier or 'No supplier',
                'cost_per_unit': ing.cost_per_unit,
                'order_cost': shortfall * ing.cost_per_unit,
                'reorder_threshold': ing.reorder_threshold
            })

        # Sort by items that need ordering first
        procurement_list.sort(key=lambda x: (-x['to_order'], x['name']))

        # Output
        if options['format'] == 'text':
            self._output_text(delivery_date, procurement_list)
        else:
            self._output_csv(delivery_date, procurement_list)

    def _output_text(self, delivery_date, procurement_list):
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS(f'  PROCUREMENT SUMMARY - {delivery_date}'))
        self.stdout.write('=' * 80)

        # Items to order
        to_order = [p for p in procurement_list if p['to_order'] > 0]
        in_stock = [p for p in procurement_list if p['to_order'] == 0]

        if to_order:
            self.stdout.write('\n' + self.style.ERROR('ITEMS TO ORDER:'))
            self.stdout.write('-' * 80)
            self.stdout.write(
                f'{"Ingredient":30s} {"Required":>10s} {"In Stock":>10s} {"Order":>10s} {"Cost":>10s}'
            )
            self.stdout.write('-' * 80)

            total_order_cost = 0
            for item in to_order:
                self.stdout.write(
                    f'{item["name"]:30s} '
                    f'{item["required"]:>9.2f}{item["unit"]:>1s} '
                    f'{item["in_stock"]:>9.2f}{item["unit"]:>1s} '
                    f'{item["to_order"]:>9.2f}{item["unit"]:>1s} '
                    f'${item["order_cost"]:>8.2f}'
                )
                total_order_cost += item['order_cost']

            self.stdout.write('-' * 80)
            self.stdout.write(f'{"TOTAL ORDER COST":>64s} ${total_order_cost:>8.2f}')

        # Items in stock
        if in_stock:
            self.stdout.write('\n' + self.style.SUCCESS('ITEMS IN STOCK (no order needed):'))
            self.stdout.write('-' * 60)

            for item in in_stock:
                remaining = item['in_stock'] - item['required']
                status = ''
                if remaining <= item['reorder_threshold']:
                    status = self.style.WARNING(' (will be low)')
                self.stdout.write(
                    f'  {item["name"]:30s}  '
                    f'requires {item["required"]:.2f}, have {item["in_stock"]:.2f} '
                    f'({remaining:.2f} remaining){status}'
                )

        self.stdout.write('\n' + '=' * 80 + '\n')

    def _output_csv(self, delivery_date, procurement_list):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['PROCUREMENT SUMMARY', str(delivery_date)])
        writer.writerow([])
        writer.writerow([
            'Ingredient', 'Unit', 'Required', 'In Stock', 'To Order',
            'Supplier', 'Cost Per Unit', 'Order Cost'
        ])

        for item in procurement_list:
            writer.writerow([
                item['name'],
                item['unit'],
                f'{item["required"]:.2f}',
                f'{item["in_stock"]:.2f}',
                f'{item["to_order"]:.2f}',
                item['supplier'],
                f'{item["cost_per_unit"]:.2f}',
                f'{item["order_cost"]:.2f}'
            ])

        self.stdout.write(output.getvalue())
