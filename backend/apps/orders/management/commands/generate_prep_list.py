"""
Generate prep list for kitchen operations.

Usage:
    python manage.py generate_prep_list --date 2026-03-22
    python manage.py generate_prep_list --next-sunday
    python manage.py generate_prep_list --next-sunday --format csv
"""

import csv
import json
from datetime import date, timedelta
from io import StringIO

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, F

from apps.orders.models import Order, OrderItem
from apps.menu.models import RecipeComponent


class Command(BaseCommand):
    help = 'Generate kitchen prep list for a delivery date'

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
            choices=['text', 'csv', 'json'],
            default='text',
            help='Output format'
        )

    def handle(self, *args, **options):
        # Determine delivery date
        if options['next_sunday']:
            today = date.today()
            days_until_sunday = (6 - today.weekday()) % 7
            if days_until_sunday == 0:
                days_until_sunday = 7  # Next Sunday, not today
            delivery_date = today + timedelta(days=days_until_sunday)
        elif options['date']:
            try:
                delivery_date = date.fromisoformat(options['date'])
            except ValueError:
                raise CommandError('Invalid date format. Use YYYY-MM-DD')
        else:
            raise CommandError('Specify --date or --next-sunday')

        # Get confirmed orders for the delivery date
        orders = Order.objects.filter(
            delivery_date=delivery_date,
            status__in=[Order.Status.PENDING, Order.Status.CONFIRMED]
        ).prefetch_related('items__menu_item')

        if not orders.exists():
            self.stdout.write(
                self.style.WARNING(f'No orders found for {delivery_date}')
            )
            return

        # Aggregate meal quantities
        meal_counts = {}
        modifier_counts = {}

        for order in orders:
            for item in order.items.all():
                meal_key = item.menu_item_name
                if meal_key not in meal_counts:
                    meal_counts[meal_key] = {
                        'quantity': 0,
                        'menu_item_id': item.menu_item_id
                    }
                meal_counts[meal_key]['quantity'] += item.quantity

                # Track modifiers
                if item.modifiers_snapshot:
                    for modifier in item.modifiers_snapshot:
                        mod_name = modifier.get('name', 'Unknown')
                        if mod_name not in modifier_counts:
                            modifier_counts[mod_name] = 0
                        modifier_counts[mod_name] += item.quantity

        # Calculate ingredient requirements
        ingredient_totals = {}
        for meal_name, data in meal_counts.items():
            if data['menu_item_id']:
                components = RecipeComponent.objects.filter(
                    menu_item_id=data['menu_item_id']
                ).select_related('ingredient')

                for component in components:
                    ing_name = component.ingredient.name
                    if ing_name not in ingredient_totals:
                        ingredient_totals[ing_name] = {
                            'quantity': 0,
                            'unit': component.ingredient.unit,
                            'cost': 0
                        }
                    qty_needed = component.quantity * data['quantity']
                    ingredient_totals[ing_name]['quantity'] += qty_needed
                    ingredient_totals[ing_name]['cost'] += component.cost * data['quantity']

        # Generate output
        output_format = options['format']

        if output_format == 'text':
            self._output_text(delivery_date, orders.count(), meal_counts, modifier_counts, ingredient_totals)
        elif output_format == 'csv':
            self._output_csv(delivery_date, meal_counts, ingredient_totals)
        elif output_format == 'json':
            self._output_json(delivery_date, orders.count(), meal_counts, modifier_counts, ingredient_totals)

    def _output_text(self, delivery_date, order_count, meal_counts, modifier_counts, ingredient_totals):
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'  KITCHEN PREP LIST - {delivery_date}'))
        self.stdout.write('=' * 60)

        self.stdout.write(f'\nTotal Orders: {order_count}')
        self.stdout.write(f'Total Meals: {sum(d["quantity"] for d in meal_counts.values())}')

        # Meals section
        self.stdout.write('\n' + '-' * 40)
        self.stdout.write(self.style.SUCCESS('MEALS TO PREPARE:'))
        self.stdout.write('-' * 40)

        sorted_meals = sorted(meal_counts.items(), key=lambda x: -x[1]['quantity'])
        for meal_name, data in sorted_meals:
            self.stdout.write(f'  {data["quantity"]:4d} x  {meal_name}')

        # Modifiers section
        if modifier_counts:
            self.stdout.write('\n' + '-' * 40)
            self.stdout.write(self.style.SUCCESS('MODIFICATIONS:'))
            self.stdout.write('-' * 40)

            for mod_name, count in sorted(modifier_counts.items(), key=lambda x: -x[1]):
                self.stdout.write(f'  {count:4d} x  {mod_name}')

        # Ingredients section
        self.stdout.write('\n' + '-' * 40)
        self.stdout.write(self.style.SUCCESS('INGREDIENTS NEEDED:'))
        self.stdout.write('-' * 40)

        total_cost = 0
        for ing_name, data in sorted(ingredient_totals.items()):
            self.stdout.write(
                f'  {data["quantity"]:8.2f} {data["unit"]:6s}  {ing_name}'
            )
            total_cost += data['cost']

        self.stdout.write('\n' + '-' * 40)
        self.stdout.write(f'Estimated Ingredient Cost: ${total_cost:.2f}')
        self.stdout.write('=' * 60 + '\n')

    def _output_csv(self, delivery_date, meal_counts, ingredient_totals):
        # Meals CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['PREP LIST', str(delivery_date)])
        writer.writerow([])
        writer.writerow(['MEALS'])
        writer.writerow(['Quantity', 'Meal Name'])
        for meal_name, data in sorted(meal_counts.items(), key=lambda x: -x[1]['quantity']):
            writer.writerow([data['quantity'], meal_name])
        writer.writerow([])
        writer.writerow(['INGREDIENTS'])
        writer.writerow(['Quantity', 'Unit', 'Ingredient'])
        for ing_name, data in sorted(ingredient_totals.items()):
            writer.writerow([f'{data["quantity"]:.2f}', data['unit'], ing_name])

        self.stdout.write(output.getvalue())

    def _output_json(self, delivery_date, order_count, meal_counts, modifier_counts, ingredient_totals):
        output = {
            'delivery_date': str(delivery_date),
            'order_count': order_count,
            'total_meals': sum(d['quantity'] for d in meal_counts.values()),
            'meals': [
                {'name': name, 'quantity': data['quantity']}
                for name, data in sorted(meal_counts.items(), key=lambda x: -x[1]['quantity'])
            ],
            'modifiers': [
                {'name': name, 'quantity': qty}
                for name, qty in sorted(modifier_counts.items(), key=lambda x: -x[1])
            ],
            'ingredients': [
                {
                    'name': name,
                    'quantity': data['quantity'],
                    'unit': data['unit'],
                    'estimated_cost': round(data['cost'], 2)
                }
                for name, data in sorted(ingredient_totals.items())
            ]
        }
        self.stdout.write(json.dumps(output, indent=2))
