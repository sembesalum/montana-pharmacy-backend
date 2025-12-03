#!/usr/bin/env python3
"""
Comprehensive script to create sample data for the pharmacy admin system.
This includes all models: categories, brands, products, batches, customers, 
sales, orders, expenses, shelves, and more for complete testing.
"""

import os
import sys
import django
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta
import random
import uuid

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import (
    BusinessUser, ProductCategory, Brand, ProductType, Product, 
    ProductBatch, Banner, Order, OrderItem, Customer, Shelf, 
    ProductLocation, Sale, SaleItem, Expense
)
from subscription.models import Package, Subscription, Transaction
from users.models import User
from django.contrib.auth.hashers import make_password


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


def create_business_users():
    """Create sample business users with different roles"""
    print("\n👥 Creating business users...")
    
    users_data = [
        {
            'business_type': 'pharmacy',
            'business_name': 'City Pharmacy',
            'phone_number': '+255712345678',
            'business_location': 'Mikocheni, Dar es Salaam',
            'tin_number': 'TIN001234567',
            'password': 'password123',
            'is_verified': True,
        },
        {
            'business_type': 'pharmacy',
            'business_name': 'Health Plus Pharmacy',
            'phone_number': '+255713456789',
            'business_location': 'Masaki, Dar es Salaam',
            'tin_number': 'TIN001234568',
            'password': 'password123',
            'is_verified': True,
        },
        {
            'business_type': 'clinic',
            'business_name': 'Wellness Medical Center',
            'phone_number': '+255714567890',
            'business_location': 'Oyster Bay, Dar es Salaam',
            'tin_number': 'TIN001234569',
            'password': 'password123',
            'is_verified': True,
        },
    ]
    
    users = {}
    for user_data in users_data:
        # Create a copy to avoid modifying the original
        user_data_copy = user_data.copy()
        password = user_data_copy.pop('password')  # Extract password
        
        user, created = BusinessUser.objects.get_or_create(
            phone_number=user_data_copy['phone_number'],
            defaults=user_data_copy
        )
        
        # Update password if user already exists or if we need to ensure it's set
        if not created or (created and not user.check_password(password)):
            user.password = password  # Will be hashed by save() method
            user.is_verified = user_data_copy.get('is_verified', True)
            user.save()
        
        users[user_data['phone_number']] = user
        print(f"✅ {'Created' if created else 'Updated'} user: {user.business_name} (Password: {password})")
    
    return users


def create_categories():
    """Create product categories"""
    print("\n📁 Creating product categories...")
    
    categories_data = [
        {
            'name': 'Medicines',
            'description': 'Prescription and over-the-counter medications',
            'is_active': True,
        },
        {
            'name': 'Medical Devices',
            'description': 'Medical equipment and devices',
            'is_active': True,
        },
        {
            'name': 'Supplements',
            'description': 'Vitamins and dietary supplements',
            'is_active': True,
        },
        {
            'name': 'Personal Care',
            'description': 'Personal hygiene and care products',
            'is_active': True,
        },
        {
            'name': 'Baby Care',
            'description': 'Products for baby and infant care',
            'is_active': True,
        },
        {
            'name': 'First Aid',
            'description': 'First aid supplies and bandages',
            'is_active': True,
        },
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        print(f"✅ {'Created' if created else 'Found'} category: {category.name}")
    
    return categories


def create_brands():
    """Create product brands"""
    print("\n🏷️ Creating brands...")
    
    brands_data = [
        {'name': 'Pfizer', 'description': 'Leading pharmaceutical company', 'is_active': True},
        {'name': 'Johnson & Johnson', 'description': 'Healthcare and consumer products', 'is_active': True},
        {'name': 'GSK', 'description': 'GlaxoSmithKline pharmaceuticals', 'is_active': True},
        {'name': 'Bayer', 'description': 'Pharmaceutical and life sciences', 'is_active': True},
        {'name': 'Omron', 'description': 'Medical devices and equipment', 'is_active': True},
        {'name': 'Roche', 'description': 'Pharmaceutical and diagnostics', 'is_active': True},
        {'name': 'Novartis', 'description': 'Global healthcare company', 'is_active': True},
        {'name': 'Sanofi', 'description': 'Pharmaceutical and healthcare', 'is_active': True},
    ]
    
    brands = {}
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults=brand_data
        )
        brands[brand_data['name']] = brand
        print(f"✅ {'Created' if created else 'Found'} brand: {brand.name}")
    
    return brands


def create_product_types(categories):
    """Create product types"""
    print("\n📦 Creating product types...")
    
    product_types_data = [
        {'name': 'Pain Relief', 'category': 'Medicines'},
        {'name': 'Antibiotics', 'category': 'Medicines'},
        {'name': 'Blood Pressure', 'category': 'Medicines'},
        {'name': 'Diabetes Care', 'category': 'Medicines'},
        {'name': 'Cough & Cold', 'category': 'Medicines'},
        {'name': 'Antacids', 'category': 'Medicines'},
        {'name': 'Thermometers', 'category': 'Medical Devices'},
        {'name': 'Blood Pressure Monitors', 'category': 'Medical Devices'},
        {'name': 'Glucose Meters', 'category': 'Medical Devices'},
        {'name': 'Stethoscopes', 'category': 'Medical Devices'},
        {'name': 'Vitamins', 'category': 'Supplements'},
        {'name': 'Minerals', 'category': 'Supplements'},
        {'name': 'Protein Supplements', 'category': 'Supplements'},
        {'name': 'Shampoo', 'category': 'Personal Care'},
        {'name': 'Soap', 'category': 'Personal Care'},
        {'name': 'Toothpaste', 'category': 'Personal Care'},
        {'name': 'Diapers', 'category': 'Baby Care'},
        {'name': 'Baby Formula', 'category': 'Baby Care'},
        {'name': 'Bandages', 'category': 'First Aid'},
        {'name': 'Antiseptics', 'category': 'First Aid'},
    ]
    
    product_types = {}
    for pt_data in product_types_data:
        product_type, created = ProductType.objects.get_or_create(
            name=pt_data['name'],
            category=categories[pt_data['category']],
            defaults={'description': f'{pt_data["name"]} products', 'is_active': True}
        )
        product_types[pt_data['name']] = product_type
        print(f"✅ {'Created' if created else 'Found'} product type: {product_type.name}")
    
    return product_types


def create_products(categories, brands, product_types):
    """Create products"""
    print("\n💊 Creating products...")
    
    products_data = [
        {
            'name': 'Paracetamol 500mg Tablets',
            'description': 'Pain relief and fever reducer. Take 1-2 tablets every 4-6 hours as needed.',
            'price': Decimal('1200.00'),
            'category': 'Medicines',
            'brand': 'Pfizer',
            'product_type': 'Pain Relief',
            'subtype': 'Tablets',
            'size': '500mg',
            'stock_quantity': 500,
            'minimum_stock': 50,
            'is_active': True,
            'is_featured': True,
        },
        {
            'name': 'Amoxicillin 250mg Capsules',
            'description': 'Broad-spectrum antibiotic. Take as directed by your doctor.',
            'price': Decimal('2500.00'),
            'category': 'Medicines',
            'brand': 'GSK',
            'product_type': 'Antibiotics',
            'subtype': 'Capsules',
            'size': '250mg',
            'stock_quantity': 200,
            'minimum_stock': 30,
            'is_active': True,
            'is_featured': True,
        },
        {
            'name': 'Digital Thermometer',
            'description': 'Fast and accurate digital thermometer for body temperature measurement.',
            'price': Decimal('25000.00'),
            'category': 'Medical Devices',
            'brand': 'Omron',
            'product_type': 'Thermometers',
            'subtype': 'Digital',
            'stock_quantity': 50,
            'minimum_stock': 10,
            'is_active': True,
            'is_featured': True,
        },
        {
            'name': 'Blood Pressure Monitor',
            'description': 'Automatic blood pressure monitor with large display.',
            'price': Decimal('85000.00'),
            'category': 'Medical Devices',
            'brand': 'Omron',
            'product_type': 'Blood Pressure Monitors',
            'subtype': 'Automatic',
            'stock_quantity': 25,
            'minimum_stock': 5,
            'is_active': True,
            'is_featured': False,
        },
        {
            'name': 'Vitamin C 1000mg Tablets',
            'description': 'High potency Vitamin C for immune support.',
            'price': Decimal('3500.00'),
            'category': 'Supplements',
            'brand': 'Bayer',
            'product_type': 'Vitamins',
            'subtype': 'Tablets',
            'size': '1000mg',
            'stock_quantity': 300,
            'minimum_stock': 40,
            'is_active': True,
            'is_featured': True,
        },
        {
            'name': 'Glucose Test Strips',
            'description': 'Test strips for blood glucose monitoring.',
            'price': Decimal('15000.00'),
            'category': 'Medical Devices',
            'brand': 'Johnson & Johnson',
            'product_type': 'Glucose Meters',
            'subtype': 'Test Strips',
            'stock_quantity': 100,
            'minimum_stock': 20,
            'is_active': True,
            'is_featured': False,
        },
        {
            'name': 'Baby Diapers Size M',
            'description': 'Super absorbent baby diapers for comfortable sleep.',
            'price': Decimal('12000.00'),
            'category': 'Baby Care',
            'brand': 'Johnson & Johnson',
            'product_type': 'Diapers',
            'subtype': 'Disposable',
            'size': 'Medium',
            'stock_quantity': 150,
            'minimum_stock': 30,
            'is_active': True,
            'is_featured': False,
        },
        {
            'name': 'Antibacterial Soap',
            'description': 'Antibacterial hand soap for effective hand hygiene.',
            'price': Decimal('2500.00'),
            'category': 'Personal Care',
            'brand': 'Johnson & Johnson',
            'product_type': 'Soap',
            'subtype': 'Liquid',
            'stock_quantity': 200,
            'minimum_stock': 50,
            'is_active': True,
            'is_featured': False,
        },
        {
            'name': 'Ibuprofen 400mg Tablets',
            'description': 'Anti-inflammatory pain reliever. Take with food.',
            'price': Decimal('1800.00'),
            'category': 'Medicines',
            'brand': 'Bayer',
            'product_type': 'Pain Relief',
            'subtype': 'Tablets',
            'size': '400mg',
            'stock_quantity': 400,
            'minimum_stock': 40,
            'is_active': True,
            'is_featured': False,
        },
        {
            'name': 'Cough Syrup 100ml',
            'description': 'Relieves cough and cold symptoms. For adults.',
            'price': Decimal('4500.00'),
            'category': 'Medicines',
            'brand': 'GSK',
            'product_type': 'Cough & Cold',
            'subtype': 'Syrup',
            'size': '100ml',
            'stock_quantity': 120,
            'minimum_stock': 20,
            'is_active': True,
            'is_featured': False,
        },
        {
            'name': 'Calcium + Vitamin D Tablets',
            'description': 'Bone health supplement with calcium and vitamin D.',
            'price': Decimal('5500.00'),
            'category': 'Supplements',
            'brand': 'Roche',
            'product_type': 'Minerals',
            'subtype': 'Tablets',
            'stock_quantity': 180,
            'minimum_stock': 25,
            'is_active': True,
            'is_featured': False,
        },
        {
            'name': 'Bandage Roll 5cm',
            'description': 'Elastic bandage for wound dressing and support.',
            'price': Decimal('3500.00'),
            'category': 'First Aid',
            'brand': 'Johnson & Johnson',
            'product_type': 'Bandages',
            'subtype': 'Roll',
            'size': '5cm',
            'stock_quantity': 80,
            'minimum_stock': 15,
            'is_active': True,
            'is_featured': False,
        },
    ]
    
    products = {}
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            defaults={
                'description': prod_data['description'],
                'price': prod_data['price'],
                'category': categories[prod_data['category']],
                'brand': brands[prod_data['brand']],
                'product_type': product_types[prod_data['product_type']],
                'subtype': prod_data.get('subtype', ''),
                'size': prod_data.get('size', ''),
                'is_active': prod_data['is_active'],
                'is_featured': prod_data.get('is_featured', False),
                'stock_quantity': prod_data['stock_quantity'],
                'minimum_stock': prod_data.get('minimum_stock', 10),
            }
        )
        products[prod_data['name']] = product
        print(f"✅ {'Created' if created else 'Found'} product: {product.name}")
    
    return products


def create_product_batches(products):
    """Create product batches"""
    print("\n📦 Creating product batches...")
    
    suppliers = ['MedSupply Co.', 'PharmaDist Ltd.', 'Health Imports', 'Medical Supplies Inc.']
    
    for product in products.values():
        # Create 1-3 batches per product
        num_batches = random.randint(1, 3)
        for i in range(num_batches):
            batch_number = f"BATCH-{product.name[:5].upper()}-{i+1:03d}"
            expiry_date = datetime.now().date() + timedelta(days=random.randint(30, 365))
            cost_price = product.price * Decimal('0.6')  # 60% of selling price
            quantity = random.randint(50, 200)
            
            batch, created = ProductBatch.objects.get_or_create(
                batch_number=batch_number,
                product=product,
                defaults={
                    'supplier': random.choice(suppliers),
                    'cost_price': cost_price,
                    'selling_price': product.price,
                    'quantity_received': quantity,
                    'quantity_remaining': quantity,
                    'expiry_date': expiry_date,
                    'is_active': True,
                }
            )
            if created:
                print(f"✅ Created batch: {batch.batch_number} for {product.name}")


def create_shelves():
    """Create storage shelves"""
    print("\n🗄️ Creating shelves...")
    
    shelves_data = [
        {'name': 'Shelf A1', 'description': 'Main shelf - Medicines'},
        {'name': 'Shelf A2', 'description': 'Main shelf - Medical Devices'},
        {'name': 'Shelf B1', 'description': 'Secondary shelf - Supplements'},
        {'name': 'Shelf B2', 'description': 'Secondary shelf - Personal Care'},
        {'name': 'Shelf C1', 'description': 'Storage shelf - Baby Care'},
        {'name': 'Shelf C2', 'description': 'Storage shelf - First Aid'},
        {'name': 'Cold Storage', 'description': 'Refrigerated storage for temperature-sensitive items'},
    ]
    
    shelves = {}
    for shelf_data in shelves_data:
        shelf, created = Shelf.objects.get_or_create(
            name=shelf_data['name'],
            defaults=shelf_data
        )
        shelves[shelf_data['name']] = shelf
        print(f"✅ {'Created' if created else 'Found'} shelf: {shelf.name}")
    
    return shelves


def create_product_locations(products, shelves):
    """Create product locations on shelves"""
    print("\n📍 Creating product locations...")
    
    shelf_list = list(shelves.values())
    
    for product in products.values():
        # Assign each product to 1-2 shelves
        num_locations = random.randint(1, 2)
        selected_shelves = random.sample(shelf_list, min(num_locations, len(shelf_list)))
        
        for shelf in selected_shelves:
            location, created = ProductLocation.objects.get_or_create(
                product=product,
                shelf=shelf,
                defaults={
                    'quantity': random.randint(10, product.stock_quantity // 2),
                }
            )
            if created:
                print(f"✅ Created location: {product.name} on {shelf.name}")


def create_customers():
    """Create sample customers"""
    print("\n👤 Creating customers...")
    
    customers_data = [
        {
            'name': 'John Mwangi',
            'phone': '+255755123456',
            'email': 'john.mwangi@email.com',
            'address': '123 Main Street, Dar es Salaam',
        },
        {
            'name': 'Sarah Hassan',
            'phone': '+255755234567',
            'email': 'sarah.hassan@email.com',
            'address': '456 Business District, Arusha',
        },
        {
            'name': 'David Kimathi',
            'phone': '+255755345678',
            'email': 'david.kimathi@email.com',
            'address': '789 Health Center, Dodoma',
        },
        {
            'name': 'Amina Juma',
            'phone': '+255755456789',
            'email': 'amina.juma@email.com',
            'address': '321 Market Square, Mwanza',
        },
        {
            'name': 'Peter Otieno',
            'phone': '+255755567890',
            'email': 'peter.otieno@email.com',
            'address': '654 Hospital Road, Tanga',
        },
    ]
    
    customers = {}
    for cust_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            phone=cust_data['phone'],
            defaults=cust_data
        )
        customers[cust_data['phone']] = customer
        print(f"✅ {'Created' if created else 'Found'} customer: {customer.name}")
    
    return customers


def create_sales(customers, products, business_users):
    """Create sample sales"""
    print("\n💰 Creating sales...")
    
    payment_methods = ['CASH', 'CARD', 'MOBILE_MONEY', 'BANK_TRANSFER']
    payment_statuses = ['PAID', 'UNPAID', 'PARTIAL']
    
    # Get a salesperson
    salesperson = list(business_users.values())[0] if business_users else None
    
    for i in range(10):
        customer = random.choice(list(customers.values())) if customers else None
        sale_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        sale = Sale.objects.create(
            customer=customer,
            customer_name=customer.name if customer else 'Walk-in Customer',
            customer_phone=customer.phone if customer else '+255755000000',
            total_amount=Decimal('0.00'),
            discount=Decimal(str(random.randint(0, 5000))),
            payment_method=random.choice(payment_methods),
            payment_status=random.choice(payment_statuses),
            salesperson=salesperson,
            salesperson_name=salesperson.business_name if salesperson else None,
            sale_date=sale_date,
        )
        
        # Add 1-4 items to each sale
        num_items = random.randint(1, 4)
        selected_products = random.sample(list(products.values()), min(num_items, len(products)))
        
        sale_total = Decimal('0.00')
        for product in selected_products:
            quantity = random.randint(1, 5)
            unit_price = product.price
            total_price = unit_price * quantity
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
            sale_total += total_price
        
        sale.total_amount = sale_total - sale.discount
        sale.save()
        print(f"✅ Created sale: {sale.sale_id} - TSh {sale.total_amount}")


def create_orders(business_users, products):
    """Create sample orders"""
    print("\n📋 Creating orders...")
    
    order_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
    payment_methods = ['cash_on_delivery', 'mobile_money', 'bank_transfer']
    payment_statuses = ['pending', 'completed']
    
    addresses = [
        "123 Main Street, Dar es Salaam, Tanzania",
        "456 Business District, Arusha, Tanzania",
        "789 Health Center, Dodoma, Tanzania",
        "321 Market Square, Mwanza, Tanzania",
        "654 Hospital Road, Tanga, Tanzania",
    ]
    
    for i in range(8):
        user = random.choice(list(business_users.values())) if business_users else None
        if not user:
            continue
            
        order = Order.objects.create(
            user=user,
            delivery_address=random.choice(addresses),
            delivery_phone=user.phone_number,
            delivery_notes=f"Order notes {i+1}",
            status=random.choice(order_statuses),
            payment_method=random.choice(payment_methods),
            payment_status=random.choice(payment_statuses),
            tracking_number=f"TRK{random.randint(100000000, 999999999)}" if random.choice([True, False]) else None,
        )
        order.generate_order_number()
        
        # Add 1-3 items to each order
        num_items = random.randint(1, 3)
        selected_products = random.sample(list(products.values()), min(num_items, len(products)))
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
                product_name=product.name,
                product_description=product.description,
                category=product.category.name,
                pack_type="Piece",
            )
        
        order.calculate_totals()
        print(f"✅ Created order: {order.order_number} - {order.status}")


def create_expenses(business_users):
    """Create sample expenses"""
    print("\n💸 Creating expenses...")
    
    expense_categories = ['Office', 'Maintenance', 'Marketing', 'Utilities', 'Travel', 'Other']
    expense_statuses = ['PENDING', 'APPROVED', 'REJECTED']
    
    expenses_data = [
        {'title': 'Office Supplies Purchase', 'description': 'Purchase of office stationery and supplies', 'amount': Decimal('150000.00'), 'category': 'Office'},
        {'title': 'Equipment Maintenance', 'description': 'Monthly maintenance of medical equipment', 'amount': Decimal('250000.00'), 'category': 'Maintenance'},
        {'title': 'Marketing Campaign', 'description': 'Social media and print advertising campaign', 'amount': Decimal('300000.00'), 'category': 'Marketing'},
        {'title': 'Electricity Bill', 'description': 'Monthly electricity bill payment', 'amount': Decimal('120000.00'), 'category': 'Utilities'},
        {'title': 'Business Travel', 'description': 'Travel expenses for supplier meeting', 'amount': Decimal('180000.00'), 'category': 'Travel'},
        {'title': 'Internet Subscription', 'description': 'Monthly internet and phone subscription', 'amount': Decimal('45000.00'), 'category': 'Utilities'},
    ]
    
    for expense_data in expenses_data:
        created_by = random.choice(list(business_users.values())) if business_users else None
        approved_by = created_by if random.choice([True, False]) else None
        
        expense = Expense.objects.create(
            title=expense_data['title'],
            description=expense_data['description'],
            amount=expense_data['amount'],
            category=expense_data['category'],
            status=random.choice(expense_statuses),
            expense_date=datetime.now().date() - timedelta(days=random.randint(0, 60)),
            created_by=created_by,
            approved_by=approved_by,
        )
        print(f"✅ Created expense: {expense.title} - TSh {expense.amount}")


def create_banners():
    """Create promotional banners"""
    print("\n🎨 Creating banners...")
    
    banners_data = [
        {
            'title': 'Summer Sale - Up to 30% Off',
            'description': 'Special discounts on selected medicines and supplements',
            'image': 'https://example.com/banners/summer-sale.jpg',
            'link_url': '/products?category=medicines',
            'is_active': True,
            'order': 1,
        },
        {
            'title': 'New Arrivals - Medical Devices',
            'description': 'Check out our latest medical equipment and devices',
            'image': 'https://example.com/banners/new-arrivals.jpg',
            'link_url': '/products?category=medical-devices',
            'is_active': True,
            'order': 2,
        },
        {
            'title': 'Free Delivery on Orders Over 100,000 TSh',
            'description': 'Enjoy free delivery on all orders above 100,000 TSh',
            'image': 'https://example.com/banners/free-delivery.jpg',
            'link_url': '/orders',
            'is_active': True,
            'order': 3,
        },
    ]
    
    for banner_data in banners_data:
        banner, created = Banner.objects.get_or_create(
            title=banner_data['title'],
            defaults=banner_data
        )
        print(f"✅ {'Created' if created else 'Found'} banner: {banner.title}")


def create_packages():
    """Create subscription packages"""
    print("\n📦 Creating subscription packages...")
    
    packages_data = [
        {
            'package_id': generate_uuid(),
            'name': 'Basic Plan',
            'amount': 50000.00,
            'days': 30,
            'description': 'Basic subscription plan for 30 days',
        },
        {
            'package_id': generate_uuid(),
            'name': 'Premium Plan',
            'amount': 120000.00,
            'days': 90,
            'description': 'Premium subscription plan for 90 days',
        },
        {
            'package_id': generate_uuid(),
            'name': 'Enterprise Plan',
            'amount': 300000.00,
            'days': 365,
            'description': 'Enterprise subscription plan for 1 year',
        },
    ]
    
    packages = {}
    for package_data in packages_data:
        package, created = Package.packages.get_or_create(
            name=package_data['name'],
            defaults=package_data
        )
        packages[package_data['name']] = package
        print(f"✅ {'Created' if created else 'Found'} package: {package.name}")
    
    return packages


def create_sample_data():
    """Main function to create all sample data"""
    print("🚀 Starting comprehensive sample data creation...")
    print("=" * 60)
    
    try:
        # Create business users
        business_users = create_business_users()
        
        # Create categories
        categories = create_categories()
        
        # Create brands
        brands = create_brands()
        
        # Create product types
        product_types = create_product_types(categories)
        
        # Create products
        products = create_products(categories, brands, product_types)
        
        # Create product batches
        create_product_batches(products)
        
        # Create shelves
        shelves = create_shelves()
        
        # Create product locations
        create_product_locations(products, shelves)
        
        # Create customers
        customers = create_customers()
        
        # Create sales
        create_sales(customers, products, business_users)
        
        # Create orders
        create_orders(business_users, products)
        
        # Create expenses
        create_expenses(business_users)
        
        # Create banners
        create_banners()
        
        # Create packages
        packages = create_packages()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 Sample data creation completed!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   - Business Users: {BusinessUser.objects.count()}")
        print(f"   - Categories: {ProductCategory.objects.count()}")
        print(f"   - Brands: {Brand.objects.count()}")
        print(f"   - Product Types: {ProductType.objects.count()}")
        print(f"   - Products: {Product.objects.count()}")
        print(f"   - Product Batches: {ProductBatch.objects.count()}")
        print(f"   - Shelves: {Shelf.objects.count()}")
        print(f"   - Product Locations: {ProductLocation.objects.count()}")
        print(f"   - Customers: {Customer.objects.count()}")
        print(f"   - Sales: {Sale.objects.count()}")
        print(f"   - Sale Items: {SaleItem.objects.count()}")
        print(f"   - Orders: {Order.objects.count()}")
        print(f"   - Order Items: {OrderItem.objects.count()}")
        print(f"   - Expenses: {Expense.objects.count()}")
        print(f"   - Banners: {Banner.objects.count()}")
        print(f"   - Packages: {Package.packages.count()}")
        print(f"\n🚀 You can now test the admin dashboard with comprehensive data!")
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    create_sample_data()

