"""
Seed database with sample data for development and testing.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data first
"""

from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed database with sample data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self._clear_data()

        self.stdout.write('Seeding database...\n')

        self._create_users()
        self._create_categories()
        self._create_ingredients()
        self._create_menu_items()
        self._create_delivery_zones()
        self._create_delivery_windows()
        self._create_coupons()

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))

    def _clear_data(self):
        from apps.marketing.models import Coupon, LoyaltyPoint, ReferralHistory
        from apps.delivery.models import DeliveryZone, DeliveryWindow, DriverAssignment, RouteSummary
        from apps.orders.models import Order, Subscription
        from apps.menu.models import Category, MenuItem, Ingredient, RecipeComponent
        from apps.accounts.models import User, CustomerProfile, DeliveryAddress

        DriverAssignment.objects.all().delete()
        RouteSummary.objects.all().delete()
        LoyaltyPoint.objects.all().delete()
        ReferralHistory.objects.all().delete()
        Coupon.objects.all().delete()
        Order.objects.all().delete()
        Subscription.objects.all().delete()
        RecipeComponent.objects.all().delete()
        Ingredient.objects.all().delete()
        MenuItem.objects.all().delete()
        Category.objects.all().delete()
        DeliveryWindow.objects.all().delete()
        DeliveryZone.objects.all().delete()
        DeliveryAddress.objects.all().delete()
        CustomerProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('  Data cleared.'))

    def _create_users(self):
        from apps.accounts.models import User, CustomerProfile, DeliveryAddress

        self.stdout.write('  Creating users...')

        # Admin
        admin, created = User.objects.get_or_create(
            email='admin@welamealprep.ca',
            defaults={
                'username': 'admin',
                'first_name': 'Wela',
                'last_name': 'Admin',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'    Created admin: admin@welamealprep.ca / admin123')

        # Kitchen staff
        kitchen, created = User.objects.get_or_create(
            email='kitchen@welamealprep.ca',
            defaults={
                'username': 'kitchen',
                'first_name': 'Chef',
                'last_name': 'Kitchen',
                'role': User.Role.KITCHEN_STAFF,
                'is_staff': True,
            }
        )
        if created:
            kitchen.set_password('kitchen123')
            kitchen.save()

        # Driver
        driver, created = User.objects.get_or_create(
            email='driver@welamealprep.ca',
            defaults={
                'username': 'driver',
                'first_name': 'Dave',
                'last_name': 'Driver',
                'role': User.Role.DRIVER,
                'phone': '+16475551234',
            }
        )
        if created:
            driver.set_password('driver123')
            driver.save()

        # Test customers
        customers_data = [
            {
                'email': 'sarah@example.com',
                'username': 'sarah',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'phone': '+16475552001',
                'address': {
                    'label': 'Home',
                    'recipient_name': 'Sarah Johnson',
                    'phone': '+16475552001',
                    'street_address': '123 Lakeshore Rd E',
                    'city': 'Oakville',
                    'postal_code': 'L6J 1H3',
                },
                'points': 1500,
            },
            {
                'email': 'mike@example.com',
                'username': 'mike',
                'first_name': 'Mike',
                'last_name': 'Chen',
                'phone': '+16475552002',
                'address': {
                    'label': 'Home',
                    'recipient_name': 'Mike Chen',
                    'phone': '+16475552002',
                    'street_address': '456 Dundas St W',
                    'city': 'Burlington',
                    'postal_code': 'L7T 1G5',
                },
                'points': 3200,
            },
            {
                'email': 'lisa@example.com',
                'username': 'lisa',
                'first_name': 'Lisa',
                'last_name': 'Patel',
                'phone': '+16475552003',
                'address': {
                    'label': 'Home',
                    'recipient_name': 'Lisa Patel',
                    'phone': '+16475552003',
                    'street_address': '789 Main St',
                    'city': 'Milton',
                    'postal_code': 'L9T 1N6',
                },
                'points': 800,
            },
            {
                'email': 'james@example.com',
                'username': 'james',
                'first_name': 'James',
                'last_name': 'Wilson',
                'phone': '+16475552004',
                'address': {
                    'label': 'Office',
                    'recipient_name': 'James Wilson',
                    'phone': '+16475552004',
                    'street_address': '101 Kerr St',
                    'city': 'Oakville',
                    'postal_code': 'L6K 3A7',
                },
                'points': 5000,
            },
        ]

        for cdata in customers_data:
            user, created = User.objects.get_or_create(
                email=cdata['email'],
                defaults={
                    'username': cdata['username'],
                    'first_name': cdata['first_name'],
                    'last_name': cdata['last_name'],
                    'role': User.Role.CUSTOMER,
                    'phone': cdata['phone'],
                }
            )
            if created:
                user.set_password('customer123')
                user.save()

                # Create profile
                profile, _ = CustomerProfile.objects.get_or_create(
                    user=user,
                    defaults={'wela_points_balance': cdata['points']}
                )

                # Create delivery address
                addr = cdata['address']
                DeliveryAddress.objects.get_or_create(
                    customer=user,
                    street_address=addr['street_address'],
                    defaults={
                        'label': addr['label'],
                        'recipient_name': addr['recipient_name'],
                        'phone': addr['phone'],
                        'city': addr['city'],
                        'province': 'Ontario',
                        'postal_code': addr['postal_code'],
                        'is_default': True,
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'    Created {len(customers_data)} customers + admin/kitchen/driver'))

    def _create_categories(self):
        from apps.menu.models import Category

        self.stdout.write('  Creating menu categories...')

        categories = [
            {'name_en': 'Thai Classics', 'name_th': 'อาหารไทยคลาสสิก', 'slug': 'thai-classics', 'sort_order': 1},
            {'name_en': 'Curries', 'name_th': 'แกง', 'slug': 'curries', 'sort_order': 2},
            {'name_en': 'Stir-Fry', 'name_th': 'ผัด', 'slug': 'stir-fry', 'sort_order': 3},
            {'name_en': 'Salads & Bowls', 'name_th': 'สลัดและบาวล์', 'slug': 'salads-bowls', 'sort_order': 4},
            {'name_en': 'Soups', 'name_th': 'ซุป', 'slug': 'soups', 'sort_order': 5},
            {'name_en': 'Sides & Extras', 'name_th': 'เครื่องเคียง', 'slug': 'sides-extras', 'sort_order': 6},
        ]

        for cat_data in categories:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )

        self.stdout.write(self.style.SUCCESS(f'    Created {len(categories)} categories'))

    def _create_ingredients(self):
        from apps.menu.models import Ingredient

        self.stdout.write('  Creating ingredients...')

        ingredients = [
            {'name': 'Jasmine Rice', 'unit': 'kg', 'current_stock_qty': 50, 'reorder_threshold': 10, 'cost_per_unit': Decimal('2.50'), 'supplier': 'Thai Foods Import'},
            {'name': 'Chicken Breast', 'unit': 'kg', 'current_stock_qty': 30, 'reorder_threshold': 8, 'cost_per_unit': Decimal('12.99'), 'supplier': 'Fresh Ontario Meats'},
            {'name': 'Chicken Thigh', 'unit': 'kg', 'current_stock_qty': 25, 'reorder_threshold': 8, 'cost_per_unit': Decimal('9.99'), 'supplier': 'Fresh Ontario Meats'},
            {'name': 'Shrimp (16/20)', 'unit': 'kg', 'current_stock_qty': 15, 'reorder_threshold': 5, 'cost_per_unit': Decimal('24.99'), 'supplier': 'Ocean Fresh Seafood'},
            {'name': 'Tofu (Firm)', 'unit': 'kg', 'current_stock_qty': 20, 'reorder_threshold': 5, 'cost_per_unit': Decimal('4.50'), 'supplier': 'Local Produce Co'},
            {'name': 'Thai Basil', 'unit': 'g', 'current_stock_qty': 3000, 'reorder_threshold': 500, 'cost_per_unit': Decimal('0.05'), 'supplier': 'Thai Foods Import'},
            {'name': 'Coconut Milk', 'unit': 'l', 'current_stock_qty': 40, 'reorder_threshold': 10, 'cost_per_unit': Decimal('3.25'), 'supplier': 'Thai Foods Import'},
            {'name': 'Green Curry Paste', 'unit': 'g', 'current_stock_qty': 5000, 'reorder_threshold': 1000, 'cost_per_unit': Decimal('0.03'), 'supplier': 'Thai Foods Import'},
            {'name': 'Red Curry Paste', 'unit': 'g', 'current_stock_qty': 4000, 'reorder_threshold': 1000, 'cost_per_unit': Decimal('0.03'), 'supplier': 'Thai Foods Import'},
            {'name': 'Fish Sauce', 'unit': 'ml', 'current_stock_qty': 5000, 'reorder_threshold': 1000, 'cost_per_unit': Decimal('0.01'), 'supplier': 'Thai Foods Import'},
            {'name': 'Oyster Sauce', 'unit': 'ml', 'current_stock_qty': 3000, 'reorder_threshold': 800, 'cost_per_unit': Decimal('0.01'), 'supplier': 'Thai Foods Import'},
            {'name': 'Broccoli', 'unit': 'kg', 'current_stock_qty': 20, 'reorder_threshold': 5, 'cost_per_unit': Decimal('4.99'), 'supplier': 'Local Produce Co'},
            {'name': 'Bell Pepper (Mixed)', 'unit': 'kg', 'current_stock_qty': 15, 'reorder_threshold': 5, 'cost_per_unit': Decimal('6.99'), 'supplier': 'Local Produce Co'},
            {'name': 'Rice Noodles', 'unit': 'kg', 'current_stock_qty': 20, 'reorder_threshold': 5, 'cost_per_unit': Decimal('3.99'), 'supplier': 'Thai Foods Import'},
            {'name': 'Peanuts (Crushed)', 'unit': 'g', 'current_stock_qty': 5000, 'reorder_threshold': 1000, 'cost_per_unit': Decimal('0.02'), 'supplier': 'Bulk Barn'},
            {'name': 'Lime', 'unit': 'unit', 'current_stock_qty': 100, 'reorder_threshold': 20, 'cost_per_unit': Decimal('0.40'), 'supplier': 'Local Produce Co'},
            {'name': 'Bean Sprouts', 'unit': 'kg', 'current_stock_qty': 10, 'reorder_threshold': 3, 'cost_per_unit': Decimal('3.99'), 'supplier': 'Local Produce Co'},
            {'name': 'Egg', 'unit': 'unit', 'current_stock_qty': 200, 'reorder_threshold': 48, 'cost_per_unit': Decimal('0.35'), 'supplier': 'Local Farms'},
            {'name': 'Sweet Potato', 'unit': 'kg', 'current_stock_qty': 15, 'reorder_threshold': 5, 'cost_per_unit': Decimal('3.99'), 'supplier': 'Local Produce Co'},
            {'name': 'Quinoa', 'unit': 'kg', 'current_stock_qty': 10, 'reorder_threshold': 3, 'cost_per_unit': Decimal('8.99'), 'supplier': 'Bulk Barn'},
        ]

        for ing_data in ingredients:
            Ingredient.objects.get_or_create(
                name=ing_data['name'],
                defaults=ing_data
            )

        self.stdout.write(self.style.SUCCESS(f'    Created {len(ingredients)} ingredients'))

    def _create_menu_items(self):
        from apps.menu.models import Category, MenuItem, MenuModifier, Ingredient, RecipeComponent

        self.stdout.write('  Creating menu items...')

        thai_classics = Category.objects.get(slug='thai-classics')
        curries = Category.objects.get(slug='curries')
        stir_fry = Category.objects.get(slug='stir-fry')
        salads = Category.objects.get(slug='salads-bowls')
        soups = Category.objects.get(slug='soups')

        menu_items = [
            {
                'category': thai_classics,
                'name_en': 'Pad Thai with Chicken',
                'name_th': 'ผัดไทยไก่',
                'description_en': 'Classic Thai stir-fried rice noodles with chicken, egg, bean sprouts, and crushed peanuts. A perfectly balanced dish.',
                'slug': 'pad-thai-chicken',
                'base_price': Decimal('14.99'),
                'calories': 520,
                'protein_g': Decimal('35.0'),
                'carbs_g': Decimal('55.0'),
                'fat_g': Decimal('16.0'),
                'fiber_g': Decimal('4.0'),
                'sodium_mg': 890,
                'sugar_g': Decimal('8.0'),
                'allergens': ['peanuts', 'eggs', 'soy', 'fish'],
                'is_halal': True,
                'spice_level': 1,
                'is_featured': True,
                'ingredients_list': 'Rice noodles, chicken breast, egg, bean sprouts, peanuts, green onion, lime, fish sauce, tamarind paste',
                'heating_instructions_en': 'Microwave 2-3 min or pan-fry 5 min over medium heat.',
            },
            {
                'category': thai_classics,
                'name_en': 'Thai Basil Chicken',
                'name_th': 'กะเพราไก่',
                'description_en': 'Stir-fried minced chicken with holy basil, Thai chilies, and garlic served over jasmine rice. Authentic Bangkok street food.',
                'slug': 'thai-basil-chicken',
                'base_price': Decimal('13.99'),
                'calories': 480,
                'protein_g': Decimal('38.0'),
                'carbs_g': Decimal('42.0'),
                'fat_g': Decimal('14.0'),
                'fiber_g': Decimal('3.0'),
                'sodium_mg': 850,
                'sugar_g': Decimal('5.0'),
                'allergens': ['soy', 'fish'],
                'is_gluten_free': True,
                'is_dairy_free': True,
                'is_halal': True,
                'spice_level': 2,
                'is_featured': True,
                'ingredients_list': 'Chicken thigh, Thai basil, garlic, Thai chilies, fish sauce, oyster sauce, jasmine rice',
                'heating_instructions_en': 'Microwave 2-3 min. Best with a fried egg on top!',
            },
            {
                'category': curries,
                'name_en': 'Green Curry Chicken',
                'name_th': 'แกงเขียวหวานไก่',
                'description_en': 'Aromatic green curry with tender chicken, bamboo shoots, Thai eggplant, and sweet basil in creamy coconut milk.',
                'slug': 'green-curry-chicken',
                'base_price': Decimal('14.99'),
                'calories': 510,
                'protein_g': Decimal('32.0'),
                'carbs_g': Decimal('45.0'),
                'fat_g': Decimal('22.0'),
                'fiber_g': Decimal('5.0'),
                'sodium_mg': 920,
                'sugar_g': Decimal('6.0'),
                'allergens': ['fish'],
                'is_gluten_free': True,
                'is_halal': True,
                'spice_level': 2,
                'is_featured': True,
                'ingredients_list': 'Chicken, green curry paste, coconut milk, bamboo shoots, Thai eggplant, basil, jasmine rice',
                'heating_instructions_en': 'Microwave 3 min with lid slightly open.',
            },
            {
                'category': curries,
                'name_en': 'Massaman Beef Curry',
                'name_th': 'แกงมัสมั่นเนื้อ',
                'description_en': 'Rich and aromatic Massaman curry with slow-braised beef, potato, and roasted peanuts in thick coconut sauce.',
                'slug': 'massaman-beef',
                'base_price': Decimal('16.99'),
                'calories': 580,
                'protein_g': Decimal('34.0'),
                'carbs_g': Decimal('48.0'),
                'fat_g': Decimal('26.0'),
                'fiber_g': Decimal('4.0'),
                'sodium_mg': 870,
                'sugar_g': Decimal('10.0'),
                'allergens': ['peanuts', 'fish'],
                'is_gluten_free': True,
                'is_halal': True,
                'spice_level': 1,
                'ingredients_list': 'Beef chuck, Massaman paste, coconut milk, potato, onion, peanuts, jasmine rice',
                'heating_instructions_en': 'Microwave 3-4 min or warm in a pot over medium heat for 7 min.',
            },
            {
                'category': stir_fry,
                'name_en': 'Cashew Chicken Stir-Fry',
                'name_th': 'ไก่ผัดเม็ดมะม่วงหิมพานต์',
                'description_en': 'Tender chicken stir-fried with roasted cashews, dried chilies, onion, and bell peppers in a savory sauce.',
                'slug': 'cashew-chicken',
                'base_price': Decimal('14.99'),
                'calories': 490,
                'protein_g': Decimal('36.0'),
                'carbs_g': Decimal('40.0'),
                'fat_g': Decimal('18.0'),
                'fiber_g': Decimal('3.0'),
                'sodium_mg': 810,
                'sugar_g': Decimal('7.0'),
                'allergens': ['tree nuts', 'soy'],
                'is_gluten_free': True,
                'is_dairy_free': True,
                'is_halal': True,
                'spice_level': 1,
                'is_featured': True,
                'ingredients_list': 'Chicken breast, cashew nuts, bell pepper, onion, dried chilies, soy sauce, jasmine rice',
                'heating_instructions_en': 'Microwave 2-3 min. Stir halfway through.',
            },
            {
                'category': stir_fry,
                'name_en': 'Garlic Pepper Shrimp',
                'name_th': 'กุ้งผัดกระเทียมพริกไทย',
                'description_en': 'Juicy shrimp wok-tossed with garlic, white pepper, and cilantro root. Served with jasmine rice and steamed broccoli.',
                'slug': 'garlic-pepper-shrimp',
                'base_price': Decimal('16.99'),
                'calories': 440,
                'protein_g': Decimal('38.0'),
                'carbs_g': Decimal('38.0'),
                'fat_g': Decimal('12.0'),
                'fiber_g': Decimal('4.0'),
                'sodium_mg': 780,
                'sugar_g': Decimal('3.0'),
                'allergens': ['shellfish', 'soy'],
                'is_gluten_free': True,
                'is_dairy_free': True,
                'is_halal': True,
                'spice_level': 1,
                'ingredients_list': 'Shrimp, garlic, white pepper, cilantro, soy sauce, oyster sauce, jasmine rice, broccoli',
                'heating_instructions_en': 'Microwave 2 min. Do not overcook shrimp.',
            },
            {
                'category': salads,
                'name_en': 'Thai Chicken Power Bowl',
                'name_th': 'พาวเวอร์โบวล์ไก่ไทย',
                'description_en': 'Grilled chicken over quinoa with edamame, cucumber, mango, and a zesty peanut-lime dressing. High protein bowl.',
                'slug': 'thai-chicken-power-bowl',
                'base_price': Decimal('15.99'),
                'calories': 520,
                'protein_g': Decimal('42.0'),
                'carbs_g': Decimal('45.0'),
                'fat_g': Decimal('16.0'),
                'fiber_g': Decimal('8.0'),
                'sodium_mg': 650,
                'sugar_g': Decimal('12.0'),
                'allergens': ['peanuts', 'soy'],
                'is_gluten_free': True,
                'is_dairy_free': True,
                'is_halal': True,
                'spice_level': 0,
                'ingredients_list': 'Chicken breast, quinoa, edamame, cucumber, mango, peanut-lime dressing',
                'heating_instructions_en': 'Best enjoyed cold. Let sit at room temperature 5 min before eating.',
            },
            {
                'category': soups,
                'name_en': 'Tom Yum Kung',
                'name_th': 'ต้มยำกุ้ง',
                'description_en': 'Iconic hot and sour Thai soup with shrimp, mushrooms, lemongrass, galangal, and kaffir lime leaves. Served with jasmine rice.',
                'slug': 'tom-yum-kung',
                'base_price': Decimal('15.99'),
                'calories': 380,
                'protein_g': Decimal('30.0'),
                'carbs_g': Decimal('35.0'),
                'fat_g': Decimal('12.0'),
                'fiber_g': Decimal('3.0'),
                'sodium_mg': 950,
                'sugar_g': Decimal('4.0'),
                'allergens': ['shellfish', 'fish'],
                'is_gluten_free': True,
                'is_dairy_free': True,
                'is_halal': True,
                'spice_level': 3,
                'ingredients_list': 'Shrimp, mushrooms, lemongrass, galangal, kaffir lime, fish sauce, lime juice, jasmine rice',
                'heating_instructions_en': 'Heat in pot over medium for 5-7 min. Do not boil vigorously.',
            },
        ]

        for item_data in menu_items:
            item, created = MenuItem.objects.get_or_create(
                slug=item_data['slug'],
                defaults=item_data
            )
            if created:
                # Add modifiers for some items
                if 'chicken' in item_data['slug']:
                    MenuModifier.objects.get_or_create(
                        menu_item=item,
                        name_en='Extra Protein',
                        defaults={
                            'name_th': 'โปรตีนเพิ่ม',
                            'price_delta': Decimal('3.00'),
                            'calories_delta': 120,
                            'protein_delta_g': Decimal('15.0'),
                        }
                    )
                    MenuModifier.objects.get_or_create(
                        menu_item=item,
                        name_en='Brown Rice',
                        defaults={
                            'name_th': 'ข้าวกล้อง',
                            'price_delta': Decimal('1.50'),
                            'calories_delta': 20,
                            'carbs_delta_g': Decimal('-5.0'),
                        }
                    )

        self.stdout.write(self.style.SUCCESS(f'    Created {len(menu_items)} menu items with modifiers'))

        # Create recipe components (simplified)
        self._create_recipe_components()

    def _create_recipe_components(self):
        from apps.menu.models import MenuItem, Ingredient, RecipeComponent

        try:
            chicken_breast = Ingredient.objects.get(name='Chicken Breast')
            chicken_thigh = Ingredient.objects.get(name='Chicken Thigh')
            jasmine_rice = Ingredient.objects.get(name='Jasmine Rice')
            coconut_milk = Ingredient.objects.get(name='Coconut Milk')
            green_curry_paste = Ingredient.objects.get(name='Green Curry Paste')
            thai_basil = Ingredient.objects.get(name='Thai Basil')
            rice_noodles = Ingredient.objects.get(name='Rice Noodles')
            peanuts = Ingredient.objects.get(name='Peanuts (Crushed)')
            egg = Ingredient.objects.get(name='Egg')
            shrimp = Ingredient.objects.get(name='Shrimp (16/20)')
            broccoli = Ingredient.objects.get(name='Broccoli')
            fish_sauce = Ingredient.objects.get(name='Fish Sauce')
        except Ingredient.DoesNotExist:
            return

        recipes = {
            'pad-thai-chicken': [
                (rice_noodles, Decimal('0.15')),
                (chicken_breast, Decimal('0.15')),
                (egg, Decimal('1.0')),
                (peanuts, Decimal('15.0')),
                (fish_sauce, Decimal('15.0')),
            ],
            'thai-basil-chicken': [
                (chicken_thigh, Decimal('0.18')),
                (jasmine_rice, Decimal('0.15')),
                (thai_basil, Decimal('10.0')),
                (fish_sauce, Decimal('10.0')),
            ],
            'green-curry-chicken': [
                (chicken_breast, Decimal('0.15')),
                (jasmine_rice, Decimal('0.15')),
                (coconut_milk, Decimal('0.15')),
                (green_curry_paste, Decimal('30.0')),
                (thai_basil, Decimal('5.0')),
            ],
            'garlic-pepper-shrimp': [
                (shrimp, Decimal('0.15')),
                (jasmine_rice, Decimal('0.15')),
                (broccoli, Decimal('0.10')),
                (fish_sauce, Decimal('8.0')),
            ],
        }

        for slug, components in recipes.items():
            try:
                item = MenuItem.objects.get(slug=slug)
                for ingredient, qty in components:
                    RecipeComponent.objects.get_or_create(
                        menu_item=item,
                        ingredient=ingredient,
                        defaults={'quantity': qty}
                    )
            except MenuItem.DoesNotExist:
                continue

        self.stdout.write(self.style.SUCCESS('    Created recipe components'))

    def _create_delivery_zones(self):
        from apps.delivery.models import DeliveryZone

        self.stdout.write('  Creating delivery zones...')

        zones = [
            {'postal_code_prefix': 'L6H', 'label': 'Oakville East', 'city': 'Oakville', 'delivery_fee': Decimal('0.00'), 'free_delivery_threshold': Decimal('0.00'), 'priority': 1},
            {'postal_code_prefix': 'L6J', 'label': 'Oakville Downtown', 'city': 'Oakville', 'delivery_fee': Decimal('0.00'), 'free_delivery_threshold': Decimal('0.00'), 'priority': 1},
            {'postal_code_prefix': 'L6K', 'label': 'Oakville Bronte', 'city': 'Oakville', 'delivery_fee': Decimal('0.00'), 'free_delivery_threshold': Decimal('0.00'), 'priority': 1},
            {'postal_code_prefix': 'L6L', 'label': 'Oakville West', 'city': 'Oakville', 'delivery_fee': Decimal('0.00'), 'free_delivery_threshold': Decimal('0.00'), 'priority': 1},
            {'postal_code_prefix': 'L6M', 'label': 'Oakville North', 'city': 'Oakville', 'delivery_fee': Decimal('0.00'), 'free_delivery_threshold': Decimal('0.00'), 'priority': 1},
            {'postal_code_prefix': 'L7L', 'label': 'Burlington South', 'city': 'Burlington', 'delivery_fee': Decimal('3.99'), 'free_delivery_threshold': Decimal('75.00'), 'priority': 2},
            {'postal_code_prefix': 'L7M', 'label': 'Burlington North', 'city': 'Burlington', 'delivery_fee': Decimal('3.99'), 'free_delivery_threshold': Decimal('75.00'), 'priority': 2},
            {'postal_code_prefix': 'L7N', 'label': 'Burlington Central', 'city': 'Burlington', 'delivery_fee': Decimal('3.99'), 'free_delivery_threshold': Decimal('75.00'), 'priority': 2},
            {'postal_code_prefix': 'L7R', 'label': 'Burlington Lakeshore', 'city': 'Burlington', 'delivery_fee': Decimal('3.99'), 'free_delivery_threshold': Decimal('75.00'), 'priority': 2},
            {'postal_code_prefix': 'L7T', 'label': 'Burlington Aldershot', 'city': 'Burlington', 'delivery_fee': Decimal('3.99'), 'free_delivery_threshold': Decimal('75.00'), 'priority': 2},
            {'postal_code_prefix': 'L9T', 'label': 'Milton', 'city': 'Milton', 'delivery_fee': Decimal('5.99'), 'free_delivery_threshold': Decimal('100.00'), 'priority': 3},
            {'postal_code_prefix': 'L5J', 'label': 'Mississauga Clarkson', 'city': 'Mississauga', 'delivery_fee': Decimal('5.99'), 'free_delivery_threshold': Decimal('100.00'), 'priority': 4},
            {'postal_code_prefix': 'L5H', 'label': 'Mississauga Port Credit', 'city': 'Mississauga', 'delivery_fee': Decimal('5.99'), 'free_delivery_threshold': Decimal('100.00'), 'priority': 4},
        ]

        for zone_data in zones:
            DeliveryZone.objects.get_or_create(
                postal_code_prefix=zone_data['postal_code_prefix'],
                defaults=zone_data
            )

        self.stdout.write(self.style.SUCCESS(f'    Created {len(zones)} delivery zones'))

    def _create_delivery_windows(self):
        from apps.delivery.models import DeliveryZone, DeliveryWindow

        self.stdout.write('  Creating delivery windows...')

        # Create windows for the next 4 Sundays
        today = date.today()
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7

        all_zones = list(DeliveryZone.objects.filter(is_active=True))

        for week in range(4):
            sunday = today + timedelta(days=days_until_sunday + (week * 7))
            cutoff = timezone.make_aware(
                timezone.datetime.combine(
                    sunday - timedelta(days=4),  # Wednesday cutoff
                    time(23, 59)
                )
            )

            window, created = DeliveryWindow.objects.get_or_create(
                date=sunday,
                time_start=time(15, 0),
                time_end=time(17, 0),
                defaults={
                    'max_orders': 50,
                    'current_orders': 0,
                    'is_open': True,
                    'cutoff_datetime': cutoff,
                }
            )
            if created:
                window.zones.set(all_zones)

        self.stdout.write(self.style.SUCCESS('    Created 4 weekly delivery windows'))

    def _create_coupons(self):
        from apps.marketing.models import Coupon

        self.stdout.write('  Creating coupons...')

        coupons = [
            {
                'code': 'WELCOME15',
                'description': '15% off your first order',
                'discount_type': Coupon.DiscountType.PERCENT,
                'discount_value': Decimal('15.00'),
                'is_first_order_only': True,
                'max_uses': 1000,
            },
            {
                'code': 'WELA10',
                'description': '$10 off orders over $50',
                'discount_type': Coupon.DiscountType.FIXED,
                'discount_value': Decimal('10.00'),
                'min_order_amount': Decimal('50.00'),
                'max_uses': 500,
            },
            {
                'code': 'FREEDELIVERY',
                'description': 'Free delivery on any order',
                'discount_type': Coupon.DiscountType.FREE_DELIVERY,
                'discount_value': Decimal('0.00'),
                'max_uses': 200,
            },
            {
                'code': 'THAI20',
                'description': '20% off (max $15 discount)',
                'discount_type': Coupon.DiscountType.PERCENT,
                'discount_value': Decimal('20.00'),
                'max_discount_amount': Decimal('15.00'),
                'min_order_amount': Decimal('40.00'),
                'max_uses': 300,
            },
        ]

        for coupon_data in coupons:
            Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )

        self.stdout.write(self.style.SUCCESS(f'    Created {len(coupons)} coupons'))
