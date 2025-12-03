#!/usr/bin/env python3
"""
Script to ensure all categories exist and are active
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import ProductCategory

def fix_categories():
    """Ensure all expected categories exist and are active"""
    print("=" * 60)
    print("Fixing Categories")
    print("=" * 60)
    
    expected_categories = [
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
    
    print("\n📁 Ensuring all categories exist and are active...")
    
    for cat_data in expected_categories:
        category, created = ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        
        # Ensure category is active
        if not category.is_active:
            category.is_active = True
            category.save()
            print(f"✅ Activated category: {category.name}")
        elif created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"✅ Category already exists: {category.name}")
    
    # Activate any other existing categories
    all_categories = ProductCategory.objects.all()
    for category in all_categories:
        if not category.is_active:
            category.is_active = True
            category.save()
            print(f"✅ Activated existing category: {category.name}")
    
    # Final count
    active_count = ProductCategory.objects.filter(is_active=True).count()
    total_count = ProductCategory.objects.count()
    
    print(f"\n📊 Summary:")
    print(f"   Total categories: {total_count}")
    print(f"   Active categories: {active_count}")
    
    print(f"\n📋 All Active Categories:")
    for cat in ProductCategory.objects.filter(is_active=True).order_by('name'):
        print(f"   ✅ {cat.name}")

if __name__ == '__main__':
    fix_categories()

