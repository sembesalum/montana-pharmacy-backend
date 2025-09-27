#!/usr/bin/env python3
"""
Script to create sample data for the pharmacy admin system.
This includes categories, brands, products, and orders for testing.
"""

import os
import sys
import django
from django.conf import settings
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import BusinessUser, ProductCategory, Brand, ProductType, Product, Order, OrderItem
import uuid
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample data for testing"""
    
    print("🚀 Creating sample data for pharmacy admin system...")
    
    # Get or create test users
    try:
        sales_user = BusinessUser.objects.get(phone_number='+255712345678')
        manager_user = BusinessUser.objects.get(phone_number='+255444987654')
        marketing_user = BusinessUser.objects.get(phone_number='+255987654321')
    except BusinessUser.DoesNotExist:
        print("❌ Test users not found. Please run create_test_accounts.py first.")
        return
    
    # Create Categories
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
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        print(f"✅ {'Created' if created else 'Found'} category: {category.name}")
    
    # Create Brands
    print("\n🏷️ Creating brands...")
    brands_data = [
        {
            'name': 'Pfizer',
            'description': 'Leading pharmaceutical company',
            'is_active': True,
        },
        {
            'name': 'Johnson & Johnson',
            'description': 'Healthcare and consumer products',
            'is_active': True,
        },
        {
            'name': 'GSK',
            'description': 'GlaxoSmithKline pharmaceuticals',
            'is_active': True,
        },
        {
            'name': 'Bayer',
            'description': 'Pharmaceutical and life sciences',
            'is_active': True,
        },
        {
            'name': 'Omron',
            'description': 'Medical devices and equipment',
            'is_active': True,
        },
    ]
    
    brands = {}
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults=brand_data
        )
        brands[brand_data['name']] = brand
        print(f"✅ {'Created' if created else 'Found'} brand: {brand.name}")
    
    # Create Product Types
    print("\n📦 Creating product types...")
    product_types_data = [
        {'name': 'Pain Relief', 'category': 'Medicines'},
        {'name': 'Antibiotics', 'category': 'Medicines'},
        {'name': 'Blood Pressure', 'category': 'Medicines'},
        {'name': 'Diabetes Care', 'category': 'Medicines'},
        {'name': 'Thermometers', 'category': 'Medical Devices'},
        {'name': 'Blood Pressure Monitors', 'category': 'Medical Devices'},
        {'name': 'Glucose Meters', 'category': 'Medical Devices'},
        {'name': 'Vitamins', 'category': 'Supplements'},
        {'name': 'Minerals', 'category': 'Supplements'},
        {'name': 'Shampoo', 'category': 'Personal Care'},
        {'name': 'Soap', 'category': 'Personal Care'},
        {'name': 'Diapers', 'category': 'Baby Care'},
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
    
    # Create Products
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
            'is_active': True,
            'is_featured': True,
            'stock_quantity': 500,
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
            'is_active': True,
            'is_featured': True,
            'stock_quantity': 200,
        },
        {
            'name': 'Digital Thermometer',
            'description': 'Fast and accurate digital thermometer for body temperature measurement.',
            'price': Decimal('25000.00'),
            'category': 'Medical Devices',
            'brand': 'Omron',
            'product_type': 'Thermometers',
            'subtype': 'Digital',
            'is_active': True,
            'is_featured': True,
            'stock_quantity': 50,
        },
        {
            'name': 'Blood Pressure Monitor',
            'description': 'Automatic blood pressure monitor with large display.',
            'price': Decimal('85000.00'),
            'category': 'Medical Devices',
            'brand': 'Omron',
            'product_type': 'Blood Pressure Monitors',
            'subtype': 'Automatic',
            'is_active': True,
            'is_featured': False,
            'stock_quantity': 25,
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
            'is_active': True,
            'is_featured': True,
            'stock_quantity': 300,
        },
        {
            'name': 'Glucose Test Strips',
            'description': 'Test strips for blood glucose monitoring.',
            'price': Decimal('15000.00'),
            'category': 'Medical Devices',
            'brand': 'Johnson & Johnson',
            'product_type': 'Glucose Meters',
            'subtype': 'Test Strips',
            'is_active': True,
            'is_featured': False,
            'stock_quantity': 100,
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
            'is_active': True,
            'is_featured': False,
            'stock_quantity': 150,
        },
        {
            'name': 'Antibacterial Soap',
            'description': 'Antibacterial hand soap for effective hand hygiene.',
            'price': Decimal('2500.00'),
            'category': 'Personal Care',
            'brand': 'Johnson & Johnson',
            'product_type': 'Soap',
            'subtype': 'Liquid',
            'is_active': True,
            'is_featured': False,
            'stock_quantity': 200,
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
                'is_featured': prod_data['is_featured'],
                'stock_quantity': prod_data['stock_quantity'],
            }
        )
        products[prod_data['name']] = product
        print(f"✅ {'Created' if created else 'Found'} product: {product.name}")
    
    # Create Sample Orders
    print("\n📋 Creating sample orders...")
    
    # Order 1 - Delivered
    order1 = Order.objects.create(
        user=sales_user,
        delivery_address="123 Main Street, Dar es Salaam, Tanzania",
        delivery_phone="+255712345678",
        delivery_notes="Please deliver after 2 PM",
        status="delivered",
        payment_method="cash_on_delivery",
        payment_status="completed",
        tracking_number="TRK001234567",
    )
    order1.generate_order_number()
    
    # Add items to order 1
    OrderItem.objects.create(
        order=order1,
        product=products['Paracetamol 500mg Tablets'],
        quantity=2,
        unit_price=products['Paracetamol 500mg Tablets'].price,
        product_name=products['Paracetamol 500mg Tablets'].name,
        product_description=products['Paracetamol 500mg Tablets'].description,
        category=products['Paracetamol 500mg Tablets'].category.name,
        pack_type="Piece",
    )
    
    OrderItem.objects.create(
        order=order1,
        product=products['Digital Thermometer'],
        quantity=1,
        unit_price=products['Digital Thermometer'].price,
        product_name=products['Digital Thermometer'].name,
        product_description=products['Digital Thermometer'].description,
        category=products['Digital Thermometer'].category.name,
        pack_type="Piece",
    )
    
    order1.calculate_totals()
    print(f"✅ Created order: {order1.order_number} - {order1.status}")
    
    # Order 2 - Pending
    order2 = Order.objects.create(
        user=marketing_user,
        delivery_address="456 Business District, Arusha, Tanzania",
        delivery_phone="+255987654321",
        status="pending",
        payment_method="mobile_money",
        payment_status="pending",
    )
    order2.generate_order_number()
    
    OrderItem.objects.create(
        order=order2,
        product=products['Amoxicillin 250mg Capsules'],
        quantity=1,
        unit_price=products['Amoxicillin 250mg Capsules'].price,
        product_name=products['Amoxicillin 250mg Capsules'].name,
        product_description=products['Amoxicillin 250mg Capsules'].description,
        category=products['Amoxicillin 250mg Capsules'].category.name,
        pack_type="Piece",
    )
    
    order2.calculate_totals()
    print(f"✅ Created order: {order2.order_number} - {order2.status}")
    
    # Order 3 - Processing
    order3 = Order.objects.create(
        user=manager_user,
        delivery_address="789 Health Center, Dodoma, Tanzania",
        delivery_phone="+255444987654",
        status="processing",
        payment_method="cash_on_delivery",
        payment_status="pending",
    )
    order3.generate_order_number()
    
    OrderItem.objects.create(
        order=order3,
        product=products['Blood Pressure Monitor'],
        quantity=1,
        unit_price=products['Blood Pressure Monitor'].price,
        product_name=products['Blood Pressure Monitor'].name,
        product_description=products['Blood Pressure Monitor'].description,
        category=products['Blood Pressure Monitor'].category.name,
        pack_type="Piece",
    )
    
    OrderItem.objects.create(
        order=order3,
        product=products['Vitamin C 1000mg Tablets'],
        quantity=3,
        unit_price=products['Vitamin C 1000mg Tablets'].price,
        product_name=products['Vitamin C 1000mg Tablets'].name,
        product_description=products['Vitamin C 1000mg Tablets'].description,
        category=products['Vitamin C 1000mg Tablets'].category.name,
        pack_type="Piece",
    )
    
    order3.calculate_totals()
    print(f"✅ Created order: {order3.order_number} - {order3.status}")
    
    print(f"\n🎉 Sample data creation completed!")
    print(f"📊 Summary:")
    print(f"   - Categories: {ProductCategory.objects.count()}")
    print(f"   - Brands: {Brand.objects.count()}")
    print(f"   - Product Types: {ProductType.objects.count()}")
    print(f"   - Products: {Product.objects.count()}")
    print(f"   - Orders: {Order.objects.count()}")
    print(f"   - Order Items: {OrderItem.objects.count()}")
    print(f"\n🚀 You can now test the admin dashboard with realistic data!")

if __name__ == '__main__':
    create_sample_data()
