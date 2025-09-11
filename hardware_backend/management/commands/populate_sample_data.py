from django.core.management.base import BaseCommand
from hardware_backend.models import ProductCategory, Brand, ProductType, Product, Banner
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with sample data for hardware delivery app'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Product Categories
        categories_data = [
            {
                'name': 'Machines',
                'description': 'Industrial and construction machines',
                'image': 'https://example.com/images/machines.jpg'
            },
            {
                'name': 'Aluminium',
                'description': 'Aluminium products and materials',
                'image': 'https://example.com/images/aluminium.jpg'
            },
            {
                'name': 'Tools',
                'description': 'Hand tools and power tools',
                'image': 'https://example.com/images/tools.jpg'
            },
            {
                'name': 'Electrical',
                'description': 'Electrical equipment and supplies',
                'image': 'https://example.com/images/electrical.jpg'
            },
            {
                'name': 'Plumbing',
                'description': 'Plumbing materials and fixtures',
                'image': 'https://example.com/images/plumbing.jpg'
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create Brands
        brands_data = [
            {
                'name': 'Caterpillar',
                'description': 'Heavy machinery and construction equipment',
                'logo': 'https://example.com/logos/caterpillar.png'
            },
            {
                'name': 'Komatsu',
                'description': 'Construction and mining equipment',
                'logo': 'https://example.com/logos/komatsu.png'
            },
            {
                'name': 'Alcoa',
                'description': 'Aluminium products and solutions',
                'logo': 'https://example.com/logos/alcoa.png'
            },
            {
                'name': 'Bosch',
                'description': 'Power tools and automotive parts',
                'logo': 'https://example.com/logos/bosch.png'
            },
            {
                'name': 'Makita',
                'description': 'Power tools and accessories',
                'logo': 'https://example.com/logos/makita.png'
            },
            {
                'name': 'Siemens',
                'description': 'Electrical equipment and automation',
                'logo': 'https://example.com/logos/siemens.png'
            }
        ]
        
        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults=brand_data
            )
            brands[brand_data['name']] = brand
            if created:
                self.stdout.write(f'Created brand: {brand.name}')
        
        # Create Product Types
        product_types_data = [
            # Machines category
            {'name': 'Excavators', 'category': categories['Machines'], 'image': 'https://example.com/images/excavators.jpg'},
            {'name': 'Bulldozers', 'category': categories['Machines'], 'image': 'https://example.com/images/bulldozers.jpg'},
            {'name': 'Cranes', 'category': categories['Machines'], 'image': 'https://example.com/images/cranes.jpg'},
            {'name': 'Loaders', 'category': categories['Machines'], 'image': 'https://example.com/images/loaders.jpg'},
            
            # Aluminium category
            {'name': 'Aluminium Sheets', 'category': categories['Aluminium'], 'image': 'https://example.com/images/aluminium-sheets.jpg'},
            {'name': 'Aluminium Profiles', 'category': categories['Aluminium'], 'image': 'https://example.com/images/aluminium-profiles.jpg'},
            {'name': 'Aluminium Pipes', 'category': categories['Aluminium'], 'image': 'https://example.com/images/aluminium-pipes.jpg'},
            {'name': 'Aluminium Bars', 'category': categories['Aluminium'], 'image': 'https://example.com/images/aluminium-bars.jpg'},
            
            # Tools category
            {'name': 'Power Tools', 'category': categories['Tools'], 'image': 'https://example.com/images/power-tools.jpg'},
            {'name': 'Hand Tools', 'category': categories['Tools'], 'image': 'https://example.com/images/hand-tools.jpg'},
            {'name': 'Measuring Tools', 'category': categories['Tools'], 'image': 'https://example.com/images/measuring-tools.jpg'},
            {'name': 'Cutting Tools', 'category': categories['Tools'], 'image': 'https://example.com/images/cutting-tools.jpg'},
            
            # Electrical category
            {'name': 'Switches', 'category': categories['Electrical'], 'image': 'https://example.com/images/switches.jpg'},
            {'name': 'Cables', 'category': categories['Electrical'], 'image': 'https://example.com/images/cables.jpg'},
            {'name': 'Lighting', 'category': categories['Electrical'], 'image': 'https://example.com/images/lighting.jpg'},
            {'name': 'Circuit Breakers', 'category': categories['Electrical'], 'image': 'https://example.com/images/circuit-breakers.jpg'},
            
            # Plumbing category
            {'name': 'Pipes', 'category': categories['Plumbing'], 'image': 'https://example.com/images/pipes.jpg'},
            {'name': 'Fittings', 'category': categories['Plumbing'], 'image': 'https://example.com/images/fittings.jpg'},
            {'name': 'Valves', 'category': categories['Plumbing'], 'image': 'https://example.com/images/valves.jpg'},
            {'name': 'Fixtures', 'category': categories['Plumbing'], 'image': 'https://example.com/images/fixtures.jpg'}
        ]
        
        product_types = {}
        for pt_data in product_types_data:
            pt, created = ProductType.objects.get_or_create(
                name=pt_data['name'],
                category=pt_data['category'],
                defaults={'description': f'{pt_data["name"]} for {pt_data["category"].name.lower()}', 'image': pt_data['image']}
            )
            product_types[pt_data['name']] = pt
            if created:
                self.stdout.write(f'Created product type: {pt.name}')
        
        # Create Products
        products_data = [
            # Excavators
            {
                'name': 'CAT 320 Excavator',
                'description': 'Heavy-duty hydraulic excavator for construction and mining',
                'price': Decimal('150000.00'),
                'image': 'https://example.com/products/cat320.jpg',
                'category': categories['Machines'],
                'brand': brands['Caterpillar'],
                'product_type': product_types['Excavators'],
                'subtype': 'Hydraulic',
                'size': '20 ton',
                'weight': Decimal('20000.00'),
                'dimensions': '8.5m x 2.8m x 2.9m',
                'stock_quantity': 5
            },
            {
                'name': 'Komatsu PC200 Excavator',
                'description': 'Versatile excavator for various construction applications',
                'price': Decimal('120000.00'),
                'image': 'https://example.com/products/komatsu-pc200.jpg',
                'category': categories['Machines'],
                'brand': brands['Komatsu'],
                'product_type': product_types['Excavators'],
                'subtype': 'Hydraulic',
                'size': '18 ton',
                'weight': Decimal('18000.00'),
                'dimensions': '8.2m x 2.7m x 2.8m',
                'stock_quantity': 3
            },
            
            # Aluminium Sheets
            {
                'name': 'Alcoa 6061-T6 Sheet',
                'description': 'High-strength aluminium alloy sheet for structural applications',
                'price': Decimal('45.00'),
                'image': 'https://example.com/products/alcoa-6061.jpg',
                'category': categories['Aluminium'],
                'brand': brands['Alcoa'],
                'product_type': product_types['Aluminium Sheets'],
                'subtype': '6061-T6',
                'size': '4ft x 8ft x 0.125in',
                'material': 'Aluminium 6061-T6',
                'weight': Decimal('15.50'),
                'stock_quantity': 100
            },
            {
                'name': 'Alcoa 5052-H32 Sheet',
                'description': 'Corrosion-resistant aluminium sheet for marine applications',
                'price': Decimal('38.00'),
                'image': 'https://example.com/products/alcoa-5052.jpg',
                'category': categories['Aluminium'],
                'brand': brands['Alcoa'],
                'product_type': product_types['Aluminium Sheets'],
                'subtype': '5052-H32',
                'size': '4ft x 8ft x 0.080in',
                'material': 'Aluminium 5052-H32',
                'weight': Decimal('9.80'),
                'stock_quantity': 75
            },
            
            # Power Tools
            {
                'name': 'Bosch GWS 18V-10 Angle Grinder',
                'description': 'Cordless angle grinder with 18V battery system',
                'price': Decimal('299.99'),
                'image': 'https://example.com/products/bosch-gws18v.jpg',
                'category': categories['Tools'],
                'brand': brands['Bosch'],
                'product_type': product_types['Power Tools'],
                'subtype': 'Angle Grinder',
                'size': '4-1/2 inch',
                'weight': Decimal('3.20'),
                'stock_quantity': 25
            },
            {
                'name': 'Makita XPH07Z Hammer Drill',
                'description': '18V LXT Lithium-Ion Brushless Cordless 1/2" Hammer Driver-Drill',
                'price': Decimal('189.99'),
                'image': 'https://example.com/products/makita-xph07z.jpg',
                'category': categories['Tools'],
                'brand': brands['Makita'],
                'product_type': product_types['Power Tools'],
                'subtype': 'Hammer Drill',
                'size': '1/2 inch',
                'weight': Decimal('4.10'),
                'stock_quantity': 30
            },
            
            # Electrical Switches
            {
                'name': 'Siemens 3-Way Switch',
                'description': 'Commercial grade 3-way toggle switch',
                'price': Decimal('12.99'),
                'image': 'https://example.com/products/siemens-3way.jpg',
                'category': categories['Electrical'],
                'brand': brands['Siemens'],
                'product_type': product_types['Switches'],
                'subtype': 'Toggle',
                'size': 'Standard',
                'color': 'White',
                'stock_quantity': 200
            },
            
            # Plumbing Pipes
            {
                'name': 'PVC Schedule 40 Pipe',
                'description': 'Standard PVC pipe for plumbing applications',
                'price': Decimal('8.50'),
                'image': 'https://example.com/products/pvc-schedule40.jpg',
                'category': categories['Plumbing'],
                'brand': brands['Siemens'],  # Using Siemens as placeholder
                'product_type': product_types['Pipes'],
                'subtype': 'Schedule 40',
                'size': '2 inch x 10ft',
                'material': 'PVC',
                'stock_quantity': 150
            }
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create Banners
        banners_data = [
            {
                'title': 'New Excavators Arrival',
                'description': 'Latest models from Caterpillar and Komatsu',
                'image': 'https://example.com/banners/excavators-banner.jpg',
                'link_url': '/products/category/machines',
                'order': 1
            },
            {
                'title': 'Aluminium Special Offers',
                'description': 'Up to 20% off on selected aluminium products',
                'image': 'https://example.com/banners/aluminium-banner.jpg',
                'link_url': '/products/category/aluminium',
                'order': 2
            },
            {
                'title': 'Power Tools Sale',
                'description': 'Professional grade tools at competitive prices',
                'image': 'https://example.com/banners/tools-banner.jpg',
                'link_url': '/products/category/tools',
                'order': 3
            }
        ]
        
        for banner_data in banners_data:
            banner, created = Banner.objects.get_or_create(
                title=banner_data['title'],
                defaults=banner_data
            )
            if created:
                self.stdout.write(f'Created banner: {banner.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        ) 