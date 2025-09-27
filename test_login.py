#!/usr/bin/env python3
"""
Test script to verify login endpoint is working correctly
"""

import requests
import json

def test_login():
    url = "http://localhost:8000/v1/hardware/login/"
    
    # Test data
    test_data = {
        "phone_number": "+255712345678",
        "password": "sales@123"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data and 'token' in data['data']:
                print("✅ Login successful with token!")
            else:
                print("❌ Login response missing token")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
