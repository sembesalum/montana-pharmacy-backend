#!/usr/bin/env python3
"""
Test script to check the home endpoint and categories
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import ProductCategory
from hardware_backend.serializers import ProductCategorySerializer
import json

def test_categories():
    """Test categories in database"""
    print("=" * 60)
    print("Testing Categories")
    print("=" * 60)
    
    # Get all categories
    all_categories = ProductCategory.objects.all()
    print(f"\n📊 Total categories in database: {all_categories.count()}")
    
    # Get active categories
    active_categories = ProductCategory.objects.filter(is_active=True)
    print(f"✅ Active categories: {active_categories.count()}")
    
    # Get inactive categories
    inactive_categories = ProductCategory.objects.filter(is_active=False)
    print(f"❌ Inactive categories: {inactive_categories.count()}")
    
    print("\n📋 All Categories:")
    for cat in all_categories:
        status = "✅ ACTIVE" if cat.is_active else "❌ INACTIVE"
        print(f"   {status} - {cat.name} (ID: {cat.category_id})")
    
    print("\n📋 Active Categories (what endpoint returns):")
    for cat in active_categories.order_by('name'):
        print(f"   ✅ {cat.name} (ID: {cat.category_id})")
    
    # Test serializer
    print("\n🔍 Testing Serializer Output:")
    serializer = ProductCategorySerializer(active_categories, many=True)
    print(json.dumps(serializer.data, indent=2))
    
    # Simulate endpoint response
    print("\n🌐 Simulated Endpoint Response:")
    response = {
        'success': True,
        'data': {
            'categories': serializer.data,
            'brands': [],
            'banners': []
        }
    }
    print(json.dumps(response, indent=2))
    
    print(f"\n📊 Categories count in response: {len(serializer.data)}")
    
    if active_categories.count() == 0:
        print("\n⚠️  WARNING: No active categories found!")
        print("   This is why the mobile app shows 'no categories available'")
        print("   Solution: Set is_active=True for categories or modify endpoint")

if __name__ == '__main__':
    test_categories()

