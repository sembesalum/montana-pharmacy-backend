#!/usr/bin/env python3
"""
Script to create test accounts using the backend API endpoints.
This script makes HTTP requests to the production API to create test accounts.
Supports both creating new accounts and updating existing ones.
"""

import requests
import json
import time

# Production API configuration
API_BASE_URL = "https://geoclimatz.pythonanywhere.com/v1/hardware"

# Mapping of old phone numbers to new phone numbers for updates
# Format: {'role': {'old_phone': 'new_phone'}}
# IMPORTANT: The old phone number must match exactly as stored in database
# The password in account_data will be used as current_password for the update
PHONE_UPDATE_MAP = {
    'MANAGER': {
        # 'old_phone': 'new_phone'
        # Example: '+255616107670': '+255616107671'
        # Add your mapping here, e.g.:
        # '+255616107670': '+255616107671'  # Old phone → New phone
    }
}

def get_user_id_by_phone(phone_number, password):
    """
    Attempt to get user_id by trying to login.
    Note: This will trigger OTP, but we can extract user info from error responses if needed.
    For now, we'll use a different approach - try to get user data endpoint if available.
    """
    # Try login to see if user exists (will return needs_otp but user exists)
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
        
        # Even if OTP is needed, user exists - but we can't get user_id this way easily
        # We'll need to use admin endpoint or another method
        return None
    except:
        return None

def update_user_profile(user_id, account_data, current_password):
    """Update an existing user's profile"""
    try:
        update_data = {
            'current_password': current_password,
            'phone_number': account_data['phone_number'],
            'business_name': account_data['business_name'],
            'business_location': account_data['business_location'],
            'business_type': account_data['business_type'],
            'tin_number': account_data['tin_number']
        }
        
        response = requests.put(
            f"{API_BASE_URL}/users/{user_id}/update-profile/",
            json=update_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        return response
    except Exception as e:
        return None

def get_all_users():
    """Get all users from admin endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/users/",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                return result['data']
        return []
    except:
        return []

def find_user_id_by_phone(phone_number):
    """Find user_id by phone number using admin endpoint"""
    users = get_all_users()
    for user in users:
        if user.get('phone_number') == phone_number:
            return user.get('user_id')
    return None

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
            'phone_number': '+255616107670',
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
                    # Check if we need to update this account
                    role = account_data.get('role')
                    update_map = PHONE_UPDATE_MAP.get(role, {})
                    
                    # Check if this phone number is in the update map (meaning it's a new phone)
                    needs_update = False
                    old_phone = None
                    
                    for old_ph, new_ph in update_map.items():
                        if account_data['phone_number'] == new_ph:
                            needs_update = True
                            old_phone = old_ph
                            break
                    
                    if needs_update and old_phone:
                        print(f"🔄 Account exists, attempting to update phone number...")
                        print(f"   Old phone: {old_phone} → New phone: {account_data['phone_number']}")
                        
                        # Find user_id by old phone number
                        user_id = find_user_id_by_phone(old_phone)
                        
                        if user_id:
                            print(f"   Found user_id: {user_id}")
                            # Attempt to update using current password
                            update_response = update_user_profile(
                                user_id, 
                                account_data, 
                                account_data['password']  # Using same password as current
                            )
                            
                            if update_response and update_response.status_code == 200:
                                result = update_response.json()
                                if result.get('success'):
                                    print(f"✅ Successfully updated {account_data['role']} account phone number")
                                    created_accounts.append(account_data)
                                else:
                                    error_msg = f"❌ Update failed: {result.get('message', 'Unknown error')}"
                                    print(error_msg)
                                    errors.append(f"{account_data['role']}: {error_msg}")
                            else:
                                error_msg = f"❌ Update failed: {update_response.text if update_response else 'No response'}"
                                print(error_msg)
                                print(f"   Note: Update requires correct current_password")
                                errors.append(f"{account_data['role']}: Update failed - check password")
                        else:
                            print(f"⚠️  Could not find user with old phone number: {old_phone}")
                            print(f"   Skipping update - user may not exist or phone number format differs")
                            errors.append(f"{account_data['role']}: User not found with old phone {old_phone}")
                    else:
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
    print(f"\n📝 IMPORTANT: To update existing accounts:")
    print(f"   1. Find the user_id from the database or admin panel")
    print(f"   2. Use PUT /users/<user_id>/update-profile/ endpoint")
    print(f"   3. Include current_password and new phone_number in the request")
    print(f"   4. Or modify PHONE_UPDATE_MAP in this script with old→new phone mapping")
    
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

