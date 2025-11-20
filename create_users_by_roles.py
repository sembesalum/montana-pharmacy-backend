#!/usr/bin/env python3
"""
Script to create users for each role in the pharmacy admin system.
This ensures all roles (SALES, MARKETING, RECEIVER, MANAGER, ACCOUNTANT) have test accounts.
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

def create_users_by_roles():
    """Create test accounts for each role with proper business_type mapping"""
    
    # User accounts mapped to frontend roles
    # business_type values map to: SALES, MARKETING, RECEIVER, MANAGER, ACCOUNTANT
    user_accounts = [
        {
            'phone_number': '+255712345678',
            'password': 'sales@123',
            'business_name': 'Demo Sales Pharmacy',
            'business_location': 'Dar es Salaam, Tanzania',
            'business_type': 'pharmacist',  # Maps to SALES
            'tin_number': '123456789001',  # Updated to avoid conflict
            'is_verified': True,
            'frontend_role': 'SALES',
        },
        {
            'phone_number': '+255987654321',
            'password': 'marketing@123',
            'business_name': 'Demo Marketing Pharmacy',
            'business_location': 'Arusha, Tanzania',
            'business_type': 'marketing',  # Maps to MARKETING
            'tin_number': '987654321',
            'is_verified': True,
            'frontend_role': 'MARKETING',
        },
        {
            'phone_number': '+255555123456',
            'password': 'receiver@123',
            'business_name': 'Demo Receiver Pharmacy',
            'business_location': 'Mwanza, Tanzania',
            'business_type': 'inventory',  # Maps to RECEIVER
            'tin_number': '555123456',
            'is_verified': True,
            'frontend_role': 'RECEIVER',
        },
        {
            'phone_number': '+255444987654',
            'password': 'manager@123',
            'business_name': 'Demo Manager Pharmacy',
            'business_location': 'Dodoma, Tanzania',
            'business_type': 'pharmacy',  # Maps to MANAGER
            'tin_number': '444987654',
            'is_verified': True,
            'frontend_role': 'MANAGER',
        },
        {
            'phone_number': '+255333456789',
            'password': 'accountant@123',
            'business_name': 'Demo Accountant Pharmacy',
            'business_location': 'Tanga, Tanzania',
            'business_type': 'accounting',  # Maps to ACCOUNTANT
            'tin_number': '333456789',
            'is_verified': True,
            'frontend_role': 'ACCOUNTANT',
        },
        {
            'phone_number': '+255222111000',
            'password': 'unverified@123',
            'business_name': 'Unverified Test Pharmacy',
            'business_location': 'Zanzibar, Tanzania',
            'business_type': 'pharmacist',  # Maps to SALES
            'tin_number': '222111000',
            'is_verified': False,
            'frontend_role': 'SALES',
        }
    ]
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    print("=" * 70)
    print("Creating Users by Roles")
    print("=" * 70)
    print()
    
    for account_data in user_accounts:
        try:
            phone = account_data['phone_number']
            frontend_role = account_data.get('frontend_role', 'N/A')
            # Create a copy without frontend_role for database operations
            db_data = {k: v for k, v in account_data.items() if k != 'frontend_role'}
            
            # Check if user already exists
            existing_user = BusinessUser.objects.filter(phone_number=phone).first()
            
            if existing_user:
                print(f"📝 Updating existing user: {db_data['business_name']}")
                # Update existing user
                for key, value in db_data.items():
                    if key == 'password':
                        existing_user.password = make_password(value)
                    else:
                        setattr(existing_user, key, value)
                existing_user.save()
                updated_count += 1
                print(f"   ✅ Updated: {phone} | Role: {frontend_role} | Type: {db_data['business_type']}")
            else:
                # Create new user
                user = BusinessUser.objects.create(
                    user_id=str(uuid.uuid4()),
                    phone_number=db_data['phone_number'],
                    password=make_password(db_data['password']),
                    business_name=db_data['business_name'],
                    business_location=db_data['business_location'],
                    business_type=db_data['business_type'],
                    tin_number=db_data['tin_number'],
                    is_verified=db_data['is_verified'],
                )
                created_count += 1
                print(f"   ✅ Created: {phone} | Role: {frontend_role} | Type: {db_data['business_type']}")
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error with {account_data['phone_number']}: {str(e)}")
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✅ Created: {created_count} users")
    print(f"📝 Updated: {updated_count} users")
    print(f"❌ Errors: {error_count} users")
    print()
    
    print("📋 User Credentials:")
    print("=" * 70)
    
    for account in user_accounts:
        role_name = account['business_type'].title()
        status = "✅ Verified" if account['is_verified'] else "⏳ Pending Verification"
        print(f"Role: {role_name} (Frontend: {account.get('frontend_role', 'N/A')})")
        print(f"  Phone: {account['phone_number']}")
        print(f"  Password: {account['password']}")
        print(f"  Business: {account['business_name']}")
        print(f"  Status: {status}")
        print()
    
    print("=" * 70)
    print("🎉 Users created successfully!")
    print("💡 You can now use these credentials to test the admin dashboard.")
    print("⚠️  Note: The 'unverified' account will require OTP verification.")
    print("=" * 70)

if __name__ == '__main__':
    create_users_by_roles()

