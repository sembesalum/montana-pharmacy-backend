#!/usr/bin/env python3
"""
Script to test API endpoints and find the correct registration endpoint.
"""

import requests
import json

# Production API configuration
API_BASE_URL = "https://geoclimatz.pythonanywhere.com/v1/hardware"

def test_endpoints():
    """Test various API endpoints to find the correct ones"""
    
    print("🔍 Testing API endpoints...")
    print("=" * 60)
    print(f"🌐 API URL: {API_BASE_URL}")
    print("=" * 60)
    
    # Test different possible endpoints
    endpoints_to_test = [
        "/",
        "/login/",
        "/register/",
        "/admin/users/create/",
        "/admin/create-user/",
        "/users/",
        "/admin/",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{API_BASE_URL}{endpoint}"
            print(f"\n🔍 Testing: {url}")
            
            # Test GET request
            response = requests.get(url, timeout=10)
            print(f"   GET Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ GET works")
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            elif response.status_code == 405:
                print(f"   ⚠️  Method not allowed (endpoint exists but GET not supported)")
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Test login endpoint specifically
    print(f"\n🔍 Testing login endpoint...")
    try:
        login_data = {
            "phone_number": "+255712345678",
            "password": "test123"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Login Status: {response.status_code}")
        if response.status_code in [200, 400, 401]:
            print(f"   ✅ Login endpoint exists")
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response: {response.text}")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Login test error: {str(e)}")

if __name__ == '__main__':
    test_endpoints()

