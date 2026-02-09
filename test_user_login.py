#!/usr/bin/env python3
"""
Script to test user login functionality.
Tests login with various phone number formats and scenarios.
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import BusinessUser
from hardware_backend.views import normalize_phone_number
from django.contrib.auth.hashers import make_password

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://geoclimatz.pythonanywhere.com/v1/hardware')
# For local testing, use: 'http://localhost:8000/v1/hardware'

def test_login_api(phone_number, password, description=""):
    """Test login via API"""
    print(f"\n{'='*60}")
    print(f"Testing Login: {description}")
    print(f"Phone: {phone_number}")
    print(f"Password: {'*' * len(password)}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/login/",
            json={
                'phone_number': phone_number,
                'password': password
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            print(f"⚠️  Warning: Response is not JSON (Content-Type: {content_type})")
            print(f"Response text (first 500 chars): {response.text[:500]}")
            return False
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON response")
            print(f"Response text: {response.text[:500]}")
            return False
        
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            if data.get('needs_otp'):
                print(f"✅ Login successful - OTP required")
                print(f"   Message: {data.get('message')}")
                print(f"   Phone: {data.get('phone_number')}")
                return True
            elif data.get('data') and data.get('data', {}).get('token'):
                print(f"✅ Login successful - Token received")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"⚠️  Login returned success but no OTP or token")
                return False
        else:
            print(f"❌ Login failed")
            print(f"   Message: {data.get('message')}")
            if data.get('debug_info'):
                print(f"   Debug Info: {data.get('debug_info')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Cannot reach {API_BASE_URL}")
        print(f"   Make sure the server is running and accessible")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Server took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_user_in_database(phone_number, password):
    """Test if user exists in database and password is correct"""
    print(f"\n{'='*60}")
    print(f"Testing User in Database")
    print(f"Phone: {phone_number}")
    print(f"{'='*60}")
    
    normalized_phone = normalize_phone_number(phone_number)
    
    # Try to find user
    user = None
    phone_variants = [
        normalized_phone,
        phone_number,
        normalized_phone[1:] if normalized_phone.startswith('+') else f"+{normalized_phone}",
    ]
    
    found_phone = None
    for phone_variant in phone_variants:
        try:
            user = BusinessUser.objects.get(phone_number=phone_variant)
            found_phone = phone_variant
            break
        except BusinessUser.DoesNotExist:
            continue
    
    if not user:
        print(f"❌ User not found in database")
        print(f"   Tried phone formats: {phone_variants}")
        return False
    
    print(f"✅ User found: {user.business_name}")
    print(f"   Phone in DB: {user.phone_number}")
    print(f"   Found with: {found_phone}")
    print(f"   Is Verified: {user.is_verified}")
    print(f"   User ID: {user.user_id}")
    
    # Test password
    password_valid = user.check_password(password)
    print(f"   Password Valid: {password_valid}")
    
    if not password_valid:
        print(f"❌ Password check failed")
        print(f"   Note: Password in database is hashed")
        return False
    
    print(f"✅ Password is correct")
    return True

def list_all_users():
    """List all users in database"""
    print(f"\n{'='*60}")
    print(f"All Users in Database")
    print(f"{'='*60}")
    
    users = BusinessUser.objects.all().order_by('created_at')
    
    if not users.exists():
        print("No users found in database")
        return
    
    print(f"Total Users: {users.count()}\n")
    
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.business_name}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Verified: {user.is_verified}")
        print(f"   Created: {user.created_at}")
        print()

def main():
    """Main test function"""
    print("🧪 User Login Test Script")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print("=" * 60)
    
    # List all users first
    list_all_users()
    
    # Get test credentials from user
    print("\n" + "=" * 60)
    print("Enter test credentials:")
    print("=" * 60)
    
    phone = input("Phone Number: ").strip()
    password = input("Password: ").strip()
    
    if not phone or not password:
        print("❌ Phone number and password are required")
        return
    
    # Test 1: Check user in database
    print("\n" + "=" * 60)
    print("TEST 1: Database Check")
    print("=" * 60)
    db_test = test_user_in_database(phone, password)
    
    if not db_test:
        print("\n⚠️  User not found or password incorrect in database")
        print("   Cannot proceed with API test")
        return
    
    # Test 2: API Login with original phone format
    print("\n" + "=" * 60)
    print("TEST 2: API Login (Original Format)")
    print("=" * 60)
    api_test1 = test_login_api(phone, password, "Original phone format")
    
    # Test 3: API Login with normalized phone format
    normalized_phone = normalize_phone_number(phone)
    if normalized_phone != phone:
        print("\n" + "=" * 60)
        print("TEST 3: API Login (Normalized Format)")
        print("=" * 60)
        api_test2 = test_login_api(normalized_phone, password, "Normalized phone format")
    else:
        api_test2 = None
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Database Check: {'✅ PASS' if db_test else '❌ FAIL'}")
    print(f"API Login (Original): {'✅ PASS' if api_test1 else '❌ FAIL'}")
    if api_test2 is not None:
        print(f"API Login (Normalized): {'✅ PASS' if api_test2 else '❌ FAIL'}")
    
    if db_test and (api_test1 or api_test2):
        print("\n🎉 Login functionality is working!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == '__main__':
    main()
