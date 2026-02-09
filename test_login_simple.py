#!/usr/bin/env python3
"""
Simple script to test user login via API.
Usage: python test_login_simple.py <phone_number> <password>
"""

import requests
import json
import sys

# API configuration
API_BASE_URL = "https://geoclimatz.pythonanywhere.com/v1/hardware"
# For local: "http://localhost:8000/v1/hardware"

def test_login(phone_number, password):
    """Test login with phone and password"""
    print(f"🧪 Testing Login")
    print(f"Phone: {phone_number}")
    print(f"Password: {'*' * len(password)}")
    print(f"API: {API_BASE_URL}/login/")
    print("-" * 60)
    
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
        
        print(f"Status: {response.status_code}")
        
        # Check if response is JSON
        try:
            data = response.json()
        except:
            print(f"❌ Response is not JSON!")
            print(f"Response: {response.text[:500]}")
            return False
        
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            if data.get('needs_otp'):
                print(f"\n✅ SUCCESS: OTP sent!")
                print(f"   Message: {data.get('message')}")
                print(f"   Phone: {data.get('phone_number')}")
                print(f"\n📱 Next step: Verify OTP using /login-verify-otp/ endpoint")
                return True
            elif data.get('data', {}).get('token'):
                print(f"\n✅ SUCCESS: Login successful!")
                print(f"   Token: {data['data']['token'][:50]}...")
                return True
            else:
                print(f"\n⚠️  Success but no OTP or token")
                return False
        else:
            print(f"\n❌ FAILED: {data.get('message')}")
            if data.get('debug_info'):
                print(f"   Debug: {data.get('debug_info')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {API_BASE_URL}")
        print(f"   Check if server is running")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python test_login_simple.py <phone_number> <password>")
        print("\nExample:")
        print("  python test_login_simple.py +255712345678 sales@123")
        print("  python test_login_simple.py 0616107670 manager@123")
        sys.exit(1)
    
    phone = sys.argv[1]
    password = sys.argv[2]
    
    success = test_login(phone, password)
    sys.exit(0 if success else 1)
