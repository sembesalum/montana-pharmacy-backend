#!/usr/bin/env python3
"""
Test script for Hardware Backend API
Run this script to test the API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/v1/hardware"

def test_home_page():
    """Test the home page API"""
    print("Testing Home Page API...")
    response = requests.get(f"{BASE_URL}/home/")
    if response.status_code == 200:
        data = response.json()
        print("✅ Home Page API working!")
        print(f"   Categories: {len(data['data']['categories'])}")
        print(f"   Brands: {len(data['data']['brands'])}")
        print(f"   Banners: {len(data['data']['banners'])}")
    else:
        print(f"❌ Home Page API failed: {response.status_code}")
    print()

def test_products_page():
    """Test the products page API"""
    print("Testing Products Page API...")
    response = requests.get(f"{BASE_URL}/products/")
    if response.status_code == 200:
        data = response.json()
        print("✅ Products Page API working!")
        print(f"   Product Types: {len(data['data']['product_types'])}")
        total_products = sum(len(pt['products']) for pt in data['data']['product_types'])
        print(f"   Total Products: {total_products}")
    else:
        print(f"❌ Products Page API failed: {response.status_code}")
    print()

def test_user_registration():
    """Test user registration"""
    print("Testing User Registration...")
    registration_data = {
        "business_type": "manufacturing",
        "business_name": "Test Manufacturing Ltd",
        "phone_number": "+1234567890",
        "business_location": "123 Test Street, Test City",
        "tin_number": "TIN123456789",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/register/", json=registration_data)
    if response.status_code == 201:
        data = response.json()
        print("✅ User Registration working!")
        print(f"   User ID: {data['user_id']}")
        print(f"   Message: {data['message']}")
        return data['user_id'], registration_data['phone_number']
    else:
        print(f"❌ User Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None, None
    print()

def test_otp_verification(phone_number):
    """Test OTP verification (this will fail since we don't have real SMS)"""
    print("Testing OTP Verification...")
    # This will fail because we're using mock SMS
    otp_data = {
        "phone_number": phone_number,
        "otp": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/verify-otp/", json=otp_data)
    if response.status_code == 200:
        print("✅ OTP Verification working!")
    else:
        print(f"❌ OTP Verification failed (expected): {response.status_code}")
        print(f"   Response: {response.text}")
    print()

def test_user_login(phone_number):
    """Test user login"""
    print("Testing User Login...")
    login_data = {
        "phone_number": phone_number,
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    if response.status_code == 200:
        data = response.json()
        print("✅ User Login working!")
        print(f"   Business Name: {data['user']['business_name']}")
    else:
        print(f"❌ User Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
    print()

def test_get_user_data(user_id):
    """Test getting user data"""
    print("Testing Get User Data API...")
    if not user_id:
        print("⏩ Skipping Get User Data API test: user_id not available")
        print()
        return

    response = requests.post(f"{BASE_URL}/user-data/", json={"user_id": user_id})
    if response.status_code == 200:
        data = response.json()
        print("✅ Get User Data API working!")
        print(f"   Business Name: {data['user']['business_name']}")
    else:
        print(f"❌ Get User Data API failed: {response.status_code}")
        print(f"   Response: {response.text}")
    print()

def test_product_search():
    """Test product search"""
    print("Testing Product Search...")
    response = requests.get(f"{BASE_URL}/products/search/?q=excavator")
    if response.status_code == 200:
        data = response.json()
        print("✅ Product Search working!")
        print(f"   Search Results: {data['data']['count']} products found")
        for product in data['data']['products']:
            print(f"   - {product['name']}")
    else:
        print(f"❌ Product Search failed: {response.status_code}")
    print()

def main():
    """Run all tests"""
    print("🚀 Testing Hardware Backend API")
    print("=" * 50)
    
    # Test public APIs
    test_home_page()
    test_products_page()
    test_product_search()
    
    # Test user registration and login
    user_id, phone_number = test_user_registration()
    if user_id and phone_number:
        test_get_user_data(user_id)
        test_otp_verification(phone_number)
        test_user_login(phone_number)
    
    print("🎉 API Testing Complete!")
    print("\n📝 Note: OTP verification will fail because we're using mock SMS service.")
    print("   In production, integrate with a real SMS service like Twilio or AfricasTalking.")

if __name__ == "__main__":
    main() 