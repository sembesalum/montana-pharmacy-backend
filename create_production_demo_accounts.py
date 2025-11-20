#!/usr/bin/env python3
"""
Production Demo Accounts Creation Script
========================================
This script creates demo accounts for testing the pharmacy admin dashboard in production.

Usage:
    python3 create_production_demo_accounts.py

Requirements:
    - Django environment must be set up
    - Database migrations must be run
    - Run from the project root directory (where manage.py is located)
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import BusinessUser
from django.contrib.auth.hashers import make_password
import uuid
from datetime import datetime

def print_header():
    """Print script header"""
    print("\n" + "=" * 70)
    print("🚀 PRODUCTION DEMO ACCOUNTS CREATION SCRIPT")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

def print_separator():
    """Print separator line"""
    print("-" * 70)

def create_demo_accounts():
    """Create demo accounts for each role in production database"""
    
    print_header()
    
    # Demo accounts configuration
    demo_accounts = [
        {
            'phone_number': '+255712345678',
            'password': 'Sales@2024',
            'business_name': 'Demo Sales Pharmacy',
            'business_location': 'Dar es Salaam, Tanzania',
            'business_type': 'pharmacist',
            'tin_number': '123456789',
            'is_verified': True,
            'role': 'SALES',
            'description': 'Sales staff account - can sell products and process transactions'
        },
        {
            'phone_number': '+255987654321',
            'password': 'Marketing@2024',
            'business_name': 'Demo Marketing Pharmacy',
            'business_location': 'Arusha, Tanzania',
            'business_type': 'marketing',
            'tin_number': '987654321',
            'is_verified': True,
            'role': 'MARKETING',
            'description': 'Marketing staff account - can manage products and promotions'
        },
        {
            'phone_number': '+255555123456',
            'password': 'Receiver@2024',
            'business_name': 'Demo Receiver Pharmacy',
            'business_location': 'Mwanza, Tanzania',
            'business_type': 'inventory',
            'tin_number': '555123456',
            'is_verified': True,
            'role': 'RECEIVER',
            'description': 'Inventory receiver account - can receive and manage inventory'
        },
        {
            'phone_number': '+255444987654',
            'password': 'Manager@2024',
            'business_name': 'Demo Manager Pharmacy',
            'business_location': 'Dodoma, Tanzania',
            'business_type': 'pharmacy',
            'tin_number': '444987654',
            'is_verified': True,
            'role': 'MANAGER',
            'description': 'Manager account - full access to all features'
        },
        {
            'phone_number': '+255333456789',
            'password': 'Accountant@2024',
            'business_name': 'Demo Accountant Pharmacy',
            'business_location': 'Tanga, Tanzania',
            'business_type': 'accounting',
            'tin_number': '333456789',
            'is_verified': True,
            'role': 'ACCOUNTANT',
            'description': 'Accountant account - can manage finances and reports'
        },
        {
            'phone_number': '+255222111000',
            'password': 'Unverified@2024',
            'business_name': 'Unverified Demo Pharmacy',
            'business_location': 'Zanzibar, Tanzania',
            'business_type': 'pharmacist',
            'tin_number': '222111000',
            'is_verified': False,
            'role': 'UNVERIFIED',
            'description': 'Unverified account - requires OTP verification on first login'
        }
    ]
    
    created_accounts = []
    updated_accounts = []
    failed_accounts = []
    
    print("📝 Starting account creation process...\n")
    
    for i, account_data in enumerate(demo_accounts, 1):
        try:
            print(f"[{i}/{len(demo_accounts)}] Processing {account_data['role']} account...")
            print(f"   Phone: {account_data['phone_number']}")
            print(f"   Business: {account_data['business_name']}")
            
            # Check if user already exists
            existing_user = BusinessUser.objects.filter(
                phone_number=account_data['phone_number']
            ).first()
            
            if existing_user:
                print(f"   ⚠️  Account already exists, updating...")
                
                # Update existing user
                existing_user.password = make_password(account_data['password'])
                existing_user.business_name = account_data['business_name']
                existing_user.business_location = account_data['business_location']
                existing_user.business_type = account_data['business_type']
                existing_user.tin_number = account_data['tin_number']
                existing_user.is_verified = account_data['is_verified']
                existing_user.save()
                
                updated_accounts.append({
                    'account': account_data,
                    'user': existing_user
                })
                print(f"   ✅ Updated successfully")
                
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
                
                created_accounts.append({
                    'account': account_data,
                    'user': user
                })
                print(f"   ✅ Created successfully")
            
            print_separator()
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")
            failed_accounts.append({
                'account': account_data,
                'error': error_msg
            })
            print_separator()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 CREATION SUMMARY")
    print("=" * 70)
    print(f"✅ New accounts created: {len(created_accounts)}")
    print(f"🔄 Existing accounts updated: {len(updated_accounts)}")
    print(f"❌ Failed accounts: {len(failed_accounts)}")
    print("=" * 70)
    
    if failed_accounts:
        print("\n❌ FAILED ACCOUNTS:")
        for failed in failed_accounts:
            print(f"   - {failed['account']['role']} ({failed['account']['phone_number']})")
            print(f"     Error: {failed['error']}")
    
    # Print credentials
    print("\n" + "=" * 70)
    print("🔐 DEMO ACCOUNT CREDENTIALS")
    print("=" * 70)
    print("\nUse these credentials to login to the production admin dashboard:\n")
    
    for account in demo_accounts:
        status_icon = "✅" if account['is_verified'] else "⏳"
        status_text = "Verified" if account['is_verified'] else "Requires OTP Verification"
        
        print(f"Role: {account['role']}")
        print(f"Phone Number: {account['phone_number']}")
        print(f"Password: {account['password']}")
        print(f"Business Name: {account['business_name']}")
        print(f"Status: {status_icon} {status_text}")
        print(f"Description: {account['description']}")
        print_separator()
    
    # Database statistics
    try:
        total_users = BusinessUser.objects.count()
        verified_users = BusinessUser.objects.filter(is_verified=True).count()
        print(f"\n📊 DATABASE STATISTICS:")
        print(f"   Total users: {total_users}")
        print(f"   Verified users: {verified_users}")
        print(f"   Unverified users: {total_users - verified_users}")
    except Exception as e:
        print(f"\n⚠️  Could not retrieve database statistics: {str(e)}")
    
    print("\n" + "=" * 70)
    print("✅ SCRIPT COMPLETED")
    print("=" * 70)
    print("\n💡 Next Steps:")
    print("   1. Test login with the credentials above")
    print("   2. Unverified accounts will require OTP verification")
    print("   3. Manager account has full access to all features")
    print("   4. Each role has specific permissions as configured")
    print("\n" + "=" * 70 + "\n")
    
    return {
        'created': len(created_accounts),
        'updated': len(updated_accounts),
        'failed': len(failed_accounts),
        'total': len(demo_accounts)
    }

def main():
    """Main function"""
    try:
        # Verify Django setup
        from django.conf import settings
        django_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')
        print(f"📦 Django Settings Module: {django_settings_module}")
        
        # Verify database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection verified")
        
        # Create accounts
        result = create_demo_accounts()
        
        # Exit with appropriate code
        if result['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except django.core.exceptions.ImproperlyConfigured as e:
        print(f"\n❌ Django Configuration Error: {str(e)}")
        print("\n💡 Make sure you:")
        print("   1. Are running from the project root directory")
        print("   2. Have set DJANGO_SETTINGS_MODULE correctly")
        print("   3. Have installed all required dependencies")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

