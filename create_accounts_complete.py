#!/usr/bin/env python3
"""
Complete script to create test accounts via API.
This script handles database setup and account creation.
"""

import requests
import json
import time

# Production API configuration
API_BASE_URL = "https://geoclimatz.pythonanywhere.com/v1/hardware"

def test_api_health():
    """Test if the API is healthy and accessible"""
    print("🔍 Testing API health...")
    
    try:
        # Test login endpoint (should exist even if database is empty)
        response = requests.post(
            f"{API_BASE_URL}/login/",
            json={"phone_number": "test", "password": "test"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Login endpoint status: {response.status_code}")
        
        if response.status_code == 500:
            try:
                data = response.json()
                if "no such table" in data.get('message', ''):
                    print("   ⚠️  Database tables not created yet")
                    return "no_tables"
                else:
                    print(f"   ❌ Server error: {data.get('message', 'Unknown error')}")
                    return "error"
            except:
                print(f"   ❌ Server error: {response.text}")
                return "error"
        elif response.status_code in [200, 400, 401]:
            print("   ✅ API is healthy")
            return "healthy"
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            return "unknown"
            
    except Exception as e:
        print(f"   ❌ Connection error: {str(e)}")
        return "connection_error"

def create_test_accounts():
    """Create test accounts using the register endpoint"""
    
    print("\n🚀 Creating test accounts...")
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
            print(f"   Phone: {account_data['phone_number']}")
            print(f"   Business: {account_data['business_name']}")
            
            # Prepare the request data
            request_data = {
                'phone_number': account_data['phone_number'],
                'password': account_data['password'],
                'business_name': account_data['business_name'],
                'business_location': account_data['business_location'],
                'business_type': account_data['business_type'],
                'tin_number': account_data['tin_number']
            }
            
            # Make API request to register user
            response = requests.post(
                f"{API_BASE_URL}/register/",
                json=request_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                if result.get('success'):
                    created_accounts.append(account_data)
                    print(f"   ✅ Successfully created {account_data['role']} account")
                else:
                    error_msg = f"API Error: {result.get('message', 'Unknown error')}"
                    print(f"   ❌ {error_msg}")
                    errors.append(f"{account_data['role']}: {error_msg}")
            elif response.status_code == 400:
                result = response.json()
                if 'already exists' in result.get('message', '').lower():
                    print(f"   ⚠️  Account already exists, skipping...")
                    created_accounts.append(account_data)
                else:
                    error_msg = f"Validation Error: {result.get('message', 'Unknown error')}"
                    print(f"   ❌ {error_msg}")
                    errors.append(f"{account_data['role']}: {error_msg}")
            elif response.status_code == 500:
                result = response.json()
                error_msg = f"Server Error: {result.get('message', 'Unknown error')}"
                print(f"   ❌ {error_msg}")
                errors.append(f"{account_data['role']}: {error_msg}")
            else:
                error_msg = f"HTTP Error {response.status_code}: {response.text[:100]}"
                print(f"   ❌ {error_msg}")
                errors.append(f"{account_data['role']}: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network Error: {str(e)}"
            print(f"   ❌ {error_msg}")
            errors.append(f"{account_data['role']}: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected Error: {str(e)}"
            print(f"   ❌ {error_msg}")
            errors.append(f"{account_data['role']}: {error_msg}")
        
        # Small delay between requests
        time.sleep(1)
    
    return created_accounts, errors

def main():
    """Main function to create test accounts"""
    
    print("🚀 Production Test Accounts Creator (API Method)")
    print("=" * 60)
    print(f"🌐 API URL: {API_BASE_URL}")
    print("=" * 60)
    
    # Test API health
    health_status = test_api_health()
    
    if health_status == "connection_error":
        print("\n❌ Cannot connect to the API. Please check:")
        print("   - API URL is correct")
        print("   - Server is running")
        print("   - Network connection is working")
        return
    
    elif health_status == "no_tables":
        print("\n⚠️  Database tables are not created yet.")
        print("   You need to run migrations on the production server first.")
        print("\n📋 To fix this, run on your production server:")
        print("   cd /path/to/your/project")
        print("   python3 manage.py migrate")
        print("   python3 manage.py createsuperuser")
        print("\n   Then run this script again.")
        return
    
    elif health_status == "error":
        print("\n❌ API is not working properly. Please check the server logs.")
        return
    
    # API is healthy, proceed with account creation
    print("\n✅ API is healthy, proceeding with account creation...")
    
    created_accounts, errors = create_test_accounts()
    
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
    
    for account in [
        {
            'phone_number': '+255712345678',
            'password': 'sales@123',
            'role': 'SALES'
        },
        {
            'phone_number': '+255987654321',
            'password': 'marketing@123',
            'role': 'MARKETING'
        },
        {
            'phone_number': '+255555123456',
            'password': 'receiver@123',
            'role': 'RECEIVER'
        },
        {
            'phone_number': '+255444987654',
            'password': 'manager@123',
            'role': 'MANAGER'
        },
        {
            'phone_number': '+255333456789',
            'password': 'accountant@123',
            'role': 'ACCOUNTANT'
        },
        {
            'phone_number': '+255222111000',
            'password': 'unverified@123',
            'role': 'UNVERIFIED'
        }
    ]:
        status = "✅ Created" if any(acc['phone_number'] == account['phone_number'] for acc in created_accounts) else "❌ Failed"
        print(f"Role: {account['role']}")
        print(f"Phone: {account['phone_number']}")
        print(f"Password: {account['password']}")
        print(f"Status: {status}")
        print("-" * 40)
    
    if created_accounts:
        print(f"\n🚀 You can now test the production dashboard!")
        print(f"🌐 Frontend: Your deployed Vercel app")
        print(f"🌐 Backend: {API_BASE_URL}")
        print(f"💡 Note: Some accounts may need OTP verification on first login")
    else:
        print(f"\n⚠️  No accounts were created. Please check the errors above.")

if __name__ == '__main__':
    main()

