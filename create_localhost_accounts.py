#!/usr/bin/env python3
"""
Script to create accounts for localhost development.
Manager account uses phone number 0616107670.
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

def normalize_phone(phone_input):
    """Normalize phone number to include country code"""
    phone_input = str(phone_input).strip()
    
    # Check if it starts with country code
    if phone_input.startswith('0'):
        # Remove leading 0 and add +255 (Tanzania)
        return f"+255{phone_input[1:]}"
    elif phone_input.startswith('255'):
        return f"+{phone_input}"
    elif phone_input.startswith('+'):
        return phone_input
    else:
        return f"+255{phone_input}"

def create_localhost_accounts():
    """Create accounts for all roles for localhost development"""
    
    # User accounts mapped to frontend roles
    # business_type values map to: SALES, MARKETING, RECEIVER, MANAGER, ACCOUNTANT
    user_accounts = [
        {
            'phone_number': '0612345678',  # Will be normalized
            'password': 'Sales@2024',
            'business_name': 'Local Sales Pharmacy',
            'business_location': 'Dar es Salaam, Tanzania',
            'business_type': 'pharmacist',  # Maps to SALES
            'tin_number': 'TIN123456789',
            'is_verified': True,
            'frontend_role': 'SALES',
        },
        {
            'phone_number': '0698765432',
            'password': 'Marketing@2024',
            'business_name': 'Local Marketing Pharmacy',
            'business_location': 'Arusha, Tanzania',
            'business_type': 'marketing',  # Maps to MARKETING
            'tin_number': 'TIN987654321',
            'is_verified': True,
            'frontend_role': 'MARKETING',
        },
        {
            'phone_number': '0655512345',
            'password': 'Receiver@2024',
            'business_name': 'Local Receiver Pharmacy',
            'business_location': 'Mwanza, Tanzania',
            'business_type': 'inventory',  # Maps to RECEIVER
            'tin_number': 'TIN555123456',
            'is_verified': True,
            'frontend_role': 'RECEIVER',
        },
        {
            'phone_number': '0616107670',  # Manager account as requested
            'password': 'Manager@2024',
            'business_name': 'Local Manager Pharmacy',
            'business_location': 'Dodoma, Tanzania',
            'business_type': 'pharmacy',  # Maps to MANAGER
            'tin_number': 'TIN616107670',
            'is_verified': True,
            'frontend_role': 'MANAGER',
        },
        {
            'phone_number': '0633345678',
            'password': 'Accountant@2024',
            'business_name': 'Local Accountant Pharmacy',
            'business_location': 'Tanga, Tanzania',
            'business_type': 'accounting',  # Maps to ACCOUNTANT
            'tin_number': 'TIN333456789',
            'is_verified': True,
            'frontend_role': 'ACCOUNTANT',
        },
    ]
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    print("=" * 70)
    print("Creating Localhost Development Accounts")
    print("=" * 70)
    print()
    
    for account_data in user_accounts:
        try:
            phone_input = account_data['phone_number']
            phone_number = normalize_phone(phone_input)
            frontend_role = account_data.get('frontend_role', 'N/A')
            
            # Create a copy without frontend_role for database operations
            db_data = {k: v for k, v in account_data.items() if k != 'frontend_role'}
            db_data['phone_number'] = phone_number
            
            # Check if user already exists
            existing_user = BusinessUser.objects.filter(phone_number=phone_number).first()
            
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
                print(f"   ✅ Updated: {phone_number} | Role: {frontend_role} | Type: {db_data['business_type']}")
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
                print(f"   ✅ Created: {phone_number} | Role: {frontend_role} | Type: {db_data['business_type']}")
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error with {account_data['phone_number']}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✅ Created: {created_count} users")
    print(f"📝 Updated: {updated_count} users")
    print(f"❌ Errors: {error_count} users")
    print()
    
    print("📋 Account Credentials:")
    print("=" * 70)
    
    for account in user_accounts:
        phone_number = normalize_phone(account['phone_number'])
        role_name = account['frontend_role']
        status = "✅ Verified" if account['is_verified'] else "⏳ Pending Verification"
        print(f"Role: {role_name}")
        print(f"  Phone: {phone_number} (or {account['phone_number']})")
        print(f"  Password: {account['password']}")
        print(f"  Business: {account['business_name']}")
        print(f"  Status: {status}")
        print()
    
    print("=" * 70)
    print("🎉 Accounts created successfully!")
    print("💡 You can now use these credentials to login to the admin dashboard.")
    print("⚠️  Note: OTP will be required for login (if enabled).")
    print()
    print("🔑 Manager Account (as requested):")
    print(f"   Phone: {normalize_phone('0616107670')} (or 0616107670)")
    print(f"   Password: Manager@2024")
    print("=" * 70)

if __name__ == '__main__':
    create_localhost_accounts()

