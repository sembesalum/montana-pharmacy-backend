#!/usr/bin/env python3
"""
Script to create test accounts using the backend API endpoints.
This script makes HTTP requests to the production API to create test accounts.
"""

import requests
import json
import time

# Production API configuration
API_BASE_URL = "https://geoclimatz.pythonanywhere.com/v1/hardware"

def create_test_accounts_via_api():
    """Create test accounts using API endpoints"""
    
    print("🚀 Creating test accounts via API...")
    print("=" * 60)
    print(f"🌐 API URL: {API_BASE_URL}")
    print("=" * 60)
    
    # Test accounts data
    test_accounts = [
        {
            'phone_number': '+255712345678',
            'password': 'sales@123',
            'business_name': 'Demo Sales Pharmacy',
            'business_location': 'Dar es Salaam, Tanzania',
            'business_type': 'pharmacist',
            'tin_number': '123456789',
            'role': 'SALES'
        },
        {
            'phone_number': '+255987654321',
            'password': 'marketing@123',
            'business_name': 'Demo Marketing Pharmacy',
            'business_location': 'Arusha, Tanzania',
            'business_type': 'marketing',
            'tin_number': '987654321',
            'role': 'MARKETING'
        },
        {
            'phone_number': '+255555123456',
            'password': 'receiver@123',
            'business_name': 'Demo Receiver Pharmacy',
            'business_location': 'Mwanza, Tanzania',
            'business_type': 'inventory',
            'tin_number': '555123456',
            'role': 'RECEIVER'
        },
        {
            'phone_number': '+255444987654',
            'password': 'manager@123',
            'business_name': 'Demo Manager Pharmacy',
            'business_location': 'Dodoma, Tanzania',
            'business_type': 'pharmacy',
            'tin_number': '444987654',
            'role': 'MANAGER'
        },
        {
            'phone_number': '+255333456789',
            'password': 'accountant@123',
            'business_name': 'Demo Accountant Pharmacy',
            'business_location': 'Tanga, Tanzania',
            'business_type': 'accounting',
            'tin_number': '333456789',
            'role': 'ACCOUNTANT'
        },
        {
            'phone_number': '+255222111000',
            'password': 'unverified@123',
            'business_name': 'Unverified Test Pharmacy',
            'business_location': 'Zanzibar, Tanzania',
            'business_type': 'pharmacist',
            'tin_number': '222111000',
            'role': 'UNVERIFIED'
        }
    ]
    
    created_accounts = []
    errors = []
    
    for i, account_data in enumerate(test_accounts, 1):
        try:
            print(f"\n[{i}/{len(test_accounts)}] Creating {account_data['role']} account...")
            print(f"Phone: {account_data['phone_number']}")
            print(f"Business: {account_data['business_name']}")
            
            # Prepare the request data
            request_data = {
                'phone_number': account_data['phone_number'],
                'password': account_data['password'],
                'business_name': account_data['business_name'],
                'business_location': account_data['business_location'],
                'business_type': account_data['business_type'],
                'tin_number': account_data['tin_number']
            }
            
            # Make API request to create user
            response = requests.post(
                f"{API_BASE_URL}/register/",
                json=request_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                if result.get('success'):
                    created_accounts.append(account_data)
                    print(f"✅ Successfully created {account_data['role']} account")
                else:
                    error_msg = f"❌ API Error: {result.get('message', 'Unknown error')}"
                    print(error_msg)
                    errors.append(f"{account_data['role']}: {error_msg}")
            elif response.status_code == 400:
                result = response.json()
                if 'already exists' in result.get('message', '').lower():
                    print(f"⚠️  Account already exists, skipping...")
                    created_accounts.append(account_data)
                else:
                    error_msg = f"❌ Validation Error: {result.get('message', 'Unknown error')}"
                    print(error_msg)
                    errors.append(f"{account_data['role']}: {error_msg}")
            else:
                error_msg = f"❌ HTTP Error {response.status_code}: {response.text}"
                print(error_msg)
                errors.append(f"{account_data['role']}: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Network Error: {str(e)}"
            print(error_msg)
            errors.append(f"{account_data['role']}: {error_msg}")
        except Exception as e:
            error_msg = f"❌ Unexpected Error: {str(e)}"
            print(error_msg)
            errors.append(f"{account_data['role']}: {error_msg}")
        
        # Small delay between requests
        time.sleep(1)
    
    # Summary
    print(f"\n🎉 Account Creation Summary:")
    print("=" * 60)
    print(f"✅ Successfully created/verified: {len(created_accounts)} accounts")
    print(f"❌ Errors: {len(errors)} accounts")
    
    if errors:
        print(f"\n❌ Errors encountered:")
        for error in errors:
            print(f"   - {error}")
    
    print(f"\n📋 Test Account Credentials:")
    print("=" * 60)
    
    for account in test_accounts:
        role_name = account['role']
        status = "✅ Created" if account in created_accounts else "❌ Failed"
        print(f"Role: {role_name}")
        print(f"Phone: {account['phone_number']}")
        print(f"Password: {account['password']}")
        print(f"Business: {account['business_name']}")
        print(f"Status: {status}")
        print("-" * 40)
    
    print(f"\n🚀 You can now test the production dashboard!")
    print(f"🌐 Frontend: Your deployed Vercel app")
    print(f"🌐 Backend: {API_BASE_URL}")
    print(f"💡 Note: Some accounts may need OTP verification on first login")
    
    return len(created_accounts), len(errors)

def test_api_connection():
    """Test if the API is accessible"""
    try:
        print("🔍 Testing API connection...")
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ API is accessible")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Production Test Accounts Creator (API Method)")
    print("=" * 60)
    
    # Test API connection first
    if test_api_connection():
        print("\n" + "=" * 60)
        created, errors = create_test_accounts_via_api()
        
        if created > 0:
            print(f"\n🎉 Success! {created} accounts are ready for testing!")
        else:
            print(f"\n⚠️  No accounts were created. Check the errors above.")
    else:
        print("\n❌ Cannot connect to the API. Please check:")
        print("   - API URL is correct")
        print("   - Server is running")
        print("   - Network connection is working")

