#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/salum_sembe/frontend/Pharmacy Project/kipenzi_backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import Sale

try:
    # Check if Sale table exists and has any records
    sale_count = Sale.objects.count()
    print(f"Number of existing Sale records: {sale_count}")
    
    if sale_count > 0:
        print("Sample Sale records:")
        for sale in Sale.objects.all()[:3]:
            print(f"  - Sale ID: {sale.sale_id}")
            print(f"    Customer: {sale.customer_name}")
            print(f"    Total: {sale.total_amount}")
            print(f"    Created: {sale.created_at}")
            print()
    else:
        print("No existing Sale records found.")
        
except Exception as e:
    print(f"Error checking database: {e}")
    print("This might mean the Sale table doesn't exist yet or there's a connection issue.")
