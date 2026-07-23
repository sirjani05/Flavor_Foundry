from django.core.management.base import BaseCommand
from market.models import Category, Product


class Command(BaseCommand):
    help = 'Seeds initial categories and products with working high-res image URLs.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding database with fresh grocery data...'))

        categories_data = [
            {
                'name': 'Fresh Vegetables',
                'description': 'Farm-fresh, crisp organic vegetables delivered daily.',
                'image_url': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Fresh Fruits',
                'description': 'Juicy, sweet, and nutrient-dense seasonal fruits.',
                'image_url': 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Dairy & Eggs',
                'description': 'Pure farm milk, rich butter, artisanal cheeses & free-range eggs.',
                'image_url': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Bakery & Bread',
                'description': 'Artisanal sourdough, fresh croissants, and whole wheat loaves.',
                'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Beverages & Juices',
                'description': 'Cold-pressed juices, sparkling water, premium teas and coffees.',
                'image_url': 'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Snacks & Pantry',
                'description': 'Healthy nuts, organic oats, chips, and pantry staples.',
                'image_url': 'https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=600&q=80'
            },
        ]

        categories_map = {}
        for cdata in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cdata['name'],
                defaults={
                    'description': cdata['description'],
                    'image_url': cdata['image_url']
                }
            )
            cat.image_url = cdata['image_url']
            cat.save()
            categories_map[cdata['name']] = cat

        products_data = [
            # Vegetables
            {
                'name': 'Organic Red Tomatoes',
                'category': 'Fresh Vegetables',
                'price': 2.99,
                'unit': '1 kg',
                'stock_quantity': 45,
                'description': 'Vine-ripened organic red tomatoes, packed with flavor and juice. Perfect for salads, sauces, and cooking.',
                'image_url': 'https://images.unsplash.com/photo-1546470427-f5b9c4c79804?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Fresh Crisp Spinach',
                'category': 'Fresh Vegetables',
                'price': 1.89,
                'unit': '250g bunch',
                'stock_quantity': 20,
                'description': 'Tender, nutrient-rich spinach leaves freshly picked from local farms.',
                'image_url': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Organic Carrots',
                'category': 'Fresh Vegetables',
                'price': 2.49,
                'unit': '1 kg pack',
                'stock_quantity': 35,
                'description': 'Sweet and crunchy orange carrots. Great for snacking, roasting, or juicing.',
                'image_url': 'https://images.unsplash.com/photo-1447175008436-084171092e8e?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Fresh Broccoli Crown',
                'category': 'Fresh Vegetables',
                'price': 3.19,
                'unit': '500g head',
                'stock_quantity': 0, # Out of stock demonstration item
                'description': 'Vibrant green broccoli crowns packed with vitamins and minerals.',
                'image_url': 'https://images.unsplash.com/photo-1584270354949-c26b0d5b4a0c?auto=format&fit=crop&w=600&q=80'
            },

            # Fruits
            {
                'name': 'Crisp Honeycrisp Apples',
                'category': 'Fresh Fruits',
                'price': 3.99,
                'unit': '1 kg',
                'stock_quantity': 50,
                'description': 'Ultra-crisp and sweet Honeycrisp apples with a perfect balance of tartness.',
                'image_url': 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Organic Cavendish Bananas',
                'category': 'Fresh Fruits',
                'price': 1.69,
                'unit': '1 bunch (approx. 1 kg)',
                'stock_quantity': 60,
                'description': 'Rich in potassium and natural energy. Naturally ripened sweet yellow bananas.',
                'image_url': 'https://images.unsplash.com/photo-1603833665858-e61d17a86224?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Fresh Strawberries',
                'category': 'Fresh Fruits',
                'price': 4.49,
                'unit': '400g box',
                'stock_quantity': 15,
                'description': 'Fragrant, bright red strawberries full of natural sweetness.',
                'image_url': 'https://images.unsplash.com/photo-1518635017498-87f514b751ba?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Juicy Navel Oranges',
                'category': 'Fresh Fruits',
                'price': 3.29,
                'unit': '1.5 kg bag',
                'stock_quantity': 30,
                'description': 'Seedless citrus oranges bursting with fresh vitamin C.',
                'image_url': 'https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80'
            },

            # Dairy & Eggs
            {
                'name': 'Whole Farm Milk (Pasteurized)',
                'category': 'Dairy & Eggs',
                'price': 3.49,
                'unit': '2 Liters',
                'stock_quantity': 40,
                'description': 'Creamy, fresh whole milk sourced from grass-fed dairy cows.',
                'image_url': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Free-Range Organic Large Eggs',
                'category': 'Dairy & Eggs',
                'price': 4.99,
                'unit': 'Carton of 12',
                'stock_quantity': 25,
                'description': 'Farm-fresh brown eggs with golden yolks from pasture-raised hens.',
                'image_url': 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Artisanal Cheddar Cheese Block',
                'category': 'Dairy & Eggs',
                'price': 5.89,
                'unit': '300g block',
                'stock_quantity': 12,
                'description': 'Aged sharp cheddar cheese crafted with traditional creamery methods.',
                'image_url': 'https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?auto=format&fit=crop&w=600&q=80'
            },

            # Bakery
            {
                'name': 'Artisan Country Sourdough Bread',
                'category': 'Bakery & Bread',
                'price': 4.79,
                'unit': '1 loaf (600g)',
                'stock_quantity': 18,
                'description': 'Slow-fermented sourdough with a crispy crust and chewy interior.',
                'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'French Butter Croissants',
                'category': 'Bakery & Bread',
                'price': 5.49,
                'unit': 'Pack of 4',
                'stock_quantity': 10,
                'description': 'Flaky, buttery gold French croissants baked fresh every morning.',
                'image_url': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80'
            },

            # Beverages
            {
                'name': 'Cold-Pressed Orange & Mango Juice',
                'category': 'Beverages & Juices',
                'price': 3.99,
                'unit': '750ml bottle',
                'stock_quantity': 22,
                'description': '100% pure cold-pressed fruit juice with zero added sugars or preservatives.',
                'image_url': 'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Sparkling Mineral Water',
                'category': 'Beverages & Juices',
                'price': 2.19,
                'unit': '1 Liter bottle',
                'stock_quantity': 50,
                'description': 'Naturally carbonated refreshing spring mineral water.',
                'image_url': 'https://images.unsplash.com/photo-1527661591475-527312dd65f5?auto=format&fit=crop&w=600&q=80'
            },

            # Snacks
            {
                'name': 'Roasted Honey Almonds',
                'category': 'Snacks & Pantry',
                'price': 6.99,
                'unit': '250g pack',
                'stock_quantity': 30,
                'description': 'Crunchy California almonds roasted with a light honey glaze and sea salt.',
                'image_url': 'https://images.unsplash.com/photo-1508061252966-f720042436d4?auto=format&fit=crop&w=600&q=80'
            },
            {
                'name': 'Organic Rolled Oats',
                'category': 'Snacks & Pantry',
                'price': 3.79,
                'unit': '1 kg bag',
                'stock_quantity': 40,
                'description': 'Whole grain organic oats perfect for wholesome breakfast porridge and baking.',
                'image_url': 'https://images.unsplash.com/photo-1517414200057-450616a69539?auto=format&fit=crop&w=600&q=80'
            },
        ]

        for pdata in products_data:
            cat = categories_map[pdata['category']]
            prod, created = Product.objects.get_or_create(
                name=pdata['name'],
                category=cat,
                defaults={
                    'price': pdata['price'],
                    'unit': pdata['unit'],
                    'stock_quantity': pdata['stock_quantity'],
                    'description': pdata['description'],
                    'image_url': pdata['image_url'],
                    'is_active': True
                }
            )
            prod.price = pdata['price']
            prod.stock_quantity = pdata['stock_quantity']
            prod.image_url = pdata['image_url']
            prod.save()
            self.stdout.write(self.style.SUCCESS(f"Updated product image: {prod.name}"))

        self.stdout.write(self.style.SUCCESS('Successfully updated grocery product images!'))
