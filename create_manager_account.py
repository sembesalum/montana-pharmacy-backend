#!/usr/bin/env python3
"""
Script to create a manager account with phone number 0616107670
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

def create_manager_account():
    """Create a manager account with phone number 0616107670"""
    
    # Normalize phone number - add country code if needed
    phone_input = "0616107670"
    
    # Check if it starts with country code
    if phone_input.startswith('0'):
        # Remove leading 0 and add +255 (Tanzania)
        phone_number = f"+255{phone_input[1:]}"
    elif phone_input.startswith('255'):
        phone_number = f"+{phone_input}"
    elif phone_input.startswith('+'):
        phone_number = phone_input
    else:
        phone_number = f"+255{phone_input}"
    
    # Manager account data
    account_data = {
        'phone_number': phone_number,
        'password': 'Manager@2024',  # Default password
        'business_name': 'Manager Account',
        'business_location': 'Tanzania',
        'business_type': 'pharmacy',  # Maps to MANAGER role
        'tin_number': f'TIN{phone_input}',  # Generate unique TIN
        'is_verified': True,
    }
    
    print("=" * 70)
    print("Creating Manager Account")
    print("=" * 70)
    print()
    print(f"Phone Number: {phone_number}")
    print(f"Business Type: {account_data['business_type']} (Maps to MANAGER role)")
    print(f"Business Name: {account_data['business_name']}")
    print(f"Password: {account_data['password']}")
    print()
    
    try:
        # Check if user already exists
        existing_user = BusinessUser.objects.filter(phone_number=phone_number).first()
        
        if existing_user:
            print(f"📝 User with phone {phone_number} already exists!")
            print(f"   Updating existing user...")
            
            # Update existing user
            existing_user.business_name = account_data['business_name']
            existing_user.business_location = account_data['business_location']
            existing_user.business_type = account_data['business_type']
            existing_user.tin_number = account_data['tin_number']
            existing_user.is_verified = account_data['is_verified']
            existing_user.password = make_password(account_data['password'])
            existing_user.save()
            
            print(f"   ✅ Updated successfully!")
            print()
            print("📋 Updated Account Details:")
            print(f"   User ID: {existing_user.user_id}")
            print(f"   Phone: {existing_user.phone_number}")
            print(f"   Business Name: {existing_user.business_name}")
            print(f"   Business Type: {existing_user.business_type} (MANAGER)")
            print(f"   TIN Number: {existing_user.tin_number}")
            print(f"   Verified: {'Yes' if existing_user.is_verified else 'No'}")
            print(f"   Password: {account_data['password']}")
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
            
            print(f"   ✅ Created successfully!")
            print()
            print("📋 Account Details:")
            print(f"   User ID: {user.user_id}")
            print(f"   Phone: {user.phone_number}")
            print(f"   Business Name: {user.business_name}")
            print(f"   Business Type: {user.business_type} (MANAGER)")
            print(f"   TIN Number: {user.tin_number}")
            print(f"   Verified: {'Yes' if user.is_verified else 'No'}")
            print(f"   Password: {account_data['password']}")
        
        print()
        print("=" * 70)
        print("✅ Manager account ready!")
        print("=" * 70)
        print()
        print("📱 Login Credentials:")
        print(f"   Phone: {phone_number}")
        print(f"   Password: {account_data['password']}")
        print()
        print("💡 You can now use these credentials to login to the admin dashboard.")
        print("⚠️  Note: OTP will be required for login (if enabled).")
        print("=" * 70)
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    create_manager_account()

