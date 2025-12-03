#!/usr/bin/env python3
"""
Test the actual API response format
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import ProductCategory
from hardware_backend.serializers import ProductCategorySerializer
from rest_framework.test import APIRequestFactory
from hardware_backend.views import home_page

def test_api_response():
    """Test the actual API response"""
    print("=" * 60)
    print("Testing API Response Format")
    print("=" * 60)
    
    # Create a test request
    factory = APIRequestFactory()
    request = factory.get('/v1/hardware/home/')
    
    # Call the view
    response = home_page(request)
    
    # Get response data
    response_data = response.data
    
    print("\n📦 Full API Response:")
    print(json.dumps(response_data, indent=2, default=str))
    
    print("\n🔍 Response Structure Check:")
    print(f"   success: {response_data.get('success')}")
    print(f"   data exists: {'data' in response_data}")
    
    if 'data' in response_data:
        data = response_data['data']
        print(f"   categories exists: {'categories' in data}")
        print(f"   categories type: {type(data.get('categories'))}")
        print(f"   categories count: {len(data.get('categories', []))}")
        
        if data.get('categories'):
            print(f"\n📋 Categories in response:")
            for i, cat in enumerate(data['categories'], 1):
                print(f"   {i}. {cat.get('name')} (ID: {cat.get('category_id')})")
        else:
            print("\n⚠️  WARNING: categories array is empty!")
    
    print(f"\n✅ Response Status Code: {response.status_code}")
    
    # Check if response matches mobile app expectations
    print("\n🔍 Mobile App Compatibility Check:")
    if response_data.get('success') and 'data' in response_data:
        categories = response_data['data'].get('categories', [])
        if isinstance(categories, list):
            print("   ✅ Categories is a list")
            print(f"   ✅ Categories count: {len(categories)}")
            if len(categories) > 0:
                print("   ✅ Categories array is not empty")
                print("   ✅ Mobile app should be able to access categories")
            else:
                print("   ⚠️  Categories array is empty - mobile app will show 'no categories'")
        else:
            print("   ❌ Categories is not a list!")
    else:
        print("   ❌ Response structure doesn't match expected format")

if __name__ == '__main__':
    test_api_response()

