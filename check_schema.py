#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/salum_sembe/frontend/Pharmacy Project/kipenzi_backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import Product, Customer, Sale, SaleItem, Shelf, ProductLocation

try:
    # Check Product model fields
    print("=== Product Model Fields ===")
    product_fields = [field.name for field in Product._meta.fields]
    print(f"Product fields: {product_fields}")
    
    # Check if minimum_stock and expiry_date exist
    if 'minimum_stock' in product_fields:
        print("✓ minimum_stock field exists")
    else:
        print("✗ minimum_stock field missing")
        
    if 'expiry_date' in product_fields:
        print("✓ expiry_date field exists")
    else:
        print("✗ expiry_date field missing")
    
    print("\n=== Other Models ===")
    print(f"Customer model exists: {Customer is not None}")
    print(f"Sale model exists: {Sale is not None}")
    print(f"SaleItem model exists: {SaleItem is not None}")
    print(f"Shelf model exists: {Shelf is not None}")
    print(f"ProductLocation model exists: {ProductLocation is not None}")
    
    # Try to create a test record
    print("\n=== Testing Model Creation ===")
    try:
        # Test Customer creation
        test_customer = Customer.objects.create(
            name="Test Customer",
            phone="1234567890"
        )
        print(f"✓ Customer created: {test_customer.customer_id}")
        test_customer.delete()
        
        # Test Shelf creation
        test_shelf = Shelf.objects.create(
            name="Test Shelf",
            description="Test Description"
        )
        print(f"✓ Shelf created: {test_shelf.shelf_id}")
        test_shelf.delete()
        
        print("✓ All models working correctly!")
        
    except Exception as e:
        print(f"✗ Error creating test records: {e}")
        
except Exception as e:
    print(f"Error: {e}")
