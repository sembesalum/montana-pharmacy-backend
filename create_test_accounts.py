#!/usr/bin/env python3
"""
Script to create test accounts for each role in the pharmacy admin system.
Run this script to create demo accounts for testing the admin dashboard.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import BusinessUser
from django.contrib.auth.hashers import make_password
import uuid

def create_test_accounts():
    """Create test accounts for each role"""
    
    # Test accounts data
    test_accounts = [
        {
            'phone_number': '+255712345678',
            'password': 'sales@123',
            'business_name': 'Demo Sales Pharmacy',
            'business_location': 'Dar es Salaam, Tanzania',
            'business_type': 'pharmacist',
            'tin_number': '123456789',
            'is_verified': True,
        },
        {
            'phone_number': '+255987654321',
            'password': 'marketing@123',
            'business_name': 'Demo Marketing Pharmacy',
            'business_location': 'Arusha, Tanzania',
            'business_type': 'marketing',
            'tin_number': '987654321',
            'is_verified': True,
        },
        {
            'phone_number': '+255555123456',
            'password': 'receiver@123',
            'business_name': 'Demo Receiver Pharmacy',
            'business_location': 'Mwanza, Tanzania',
            'business_type': 'inventory',
            'tin_number': '555123456',
            'is_verified': True,
        },
        {
            'phone_number': '+255444987654',
            'password': 'manager@123',
            'business_name': 'Demo Manager Pharmacy',
            'business_location': 'Dodoma, Tanzania',
            'business_type': 'pharmacy',
            'tin_number': '444987654',
            'is_verified': True,
        },
        {
            'phone_number': '+255333456789',
            'password': 'accountant@123',
            'business_name': 'Demo Accountant Pharmacy',
            'business_location': 'Tanga, Tanzania',
            'business_type': 'accounting',
            'tin_number': '333456789',
            'is_verified': True,
        },
        {
            'phone_number': '+255222111000',
            'password': 'unverified@123',
            'business_name': 'Unverified Test Pharmacy',
            'business_location': 'Zanzibar, Tanzania',
            'business_type': 'pharmacist',
            'tin_number': '222111000',
            'is_verified': False,
        }
    ]
    
    created_accounts = []
    
    for account_data in test_accounts:
        try:
            # Check if user already exists
            existing_user = BusinessUser.objects.filter(phone_number=account_data['phone_number']).first()
            
            if existing_user:
                print(f"User with phone {account_data['phone_number']} already exists. Updating...")
                # Update existing user
                for key, value in account_data.items():
                    if key == 'password':
                        existing_user.password = make_password(value)
                    else:
                        setattr(existing_user, key, value)
                existing_user.save()
                created_accounts.append(existing_user)
                print(f"✅ Updated user: {account_data['business_name']} ({account_data['phone_number']})")
            else:
                # Create new user
                user = BusinessUser.objects.create(
                    user_id=str(uuid.uuid4()),
                    phone_number=account_data['phone_number'],
                    password=make_password(account_data['password']),
                    business_name=account_data['business_name'],
                    business_location=account_data['business_location'],
                    business_type=account_data['business_type'],
                    tin_number=account_data['tin_number'],
                    is_verified=account_data['is_verified'],
                )
                created_accounts.append(user)
                print(f"✅ Created user: {account_data['business_name']} ({account_data['phone_number']})")
                
        except Exception as e:
            print(f"❌ Error creating user {account_data['phone_number']}: {str(e)}")
    
    print(f"\n🎉 Successfully created/updated {len(created_accounts)} test accounts!")
    print("\n📋 Test Account Credentials:")
    print("=" * 50)
    
    for account in test_accounts:
        role_name = account['business_type'].title()
        status = "✅ Verified" if account['is_verified'] else "⏳ Pending Verification"
        print(f"Role: {role_name}")
        print(f"Phone: {account['phone_number']}")
        print(f"Password: {account['password']}")
        print(f"Business: {account['business_name']}")
        print(f"Status: {status}")
        print("-" * 30)
    
    print("\n🚀 You can now use these credentials to test the admin dashboard!")
    print("💡 Note: The 'unverified' account will require OTP verification during login.")

if __name__ == '__main__':
    create_test_accounts()
