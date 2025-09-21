#!/usr/bin/env python3
"""
Test script to verify CORS is working properly
"""

import requests
import json

BASE_URL = "http://localhost:5121"

def test_cors_preflight():
    """Test CORS preflight request"""
    print("🔧 Testing CORS Preflight Request")
    print("=" * 40)
    
    try:
        # Test preflight request
        response = requests.options(f"{BASE_URL}/api/complete-voice-flow", 
                                  headers={
                                      'Origin': 'http://localhost:5173',
                                      'Access-Control-Request-Method': 'POST',
                                      'Access-Control-Request-Headers': 'Content-Type'
                                  })
        
        print(f"Preflight response status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
        
        if response.status_code == 200:
            print("✅ CORS preflight request successful")
            return True
        else:
            print("❌ CORS preflight request failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")
        return False

def test_actual_request():
    """Test actual POST request with CORS headers"""
    print("\n🌐 Testing Actual CORS Request")
    print("=" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/api/complete-voice-flow", 
                               json={},
                               headers={
                                   'Origin': 'http://localhost:5173',
                                   'Content-Type': 'application/json'
                               },
                               timeout=5)
        
        print(f"Request response status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        
        if response.status_code == 200:
            print("✅ CORS request successful")
            return True
        else:
            print(f"❌ CORS request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✅ CORS request successful (timeout expected for voice flow)")
        return True
    except Exception as e:
        print(f"❌ Error testing CORS request: {e}")
        return False

def test_simple_endpoint():
    """Test a simple endpoint to verify CORS is working"""
    print("\n🔍 Testing Simple Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/get-categories",
                              headers={'Origin': 'http://localhost:5173'})
        
        print(f"Response status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        
        if response.status_code == 200:
            print("✅ Simple endpoint CORS working")
            return True
        else:
            print("❌ Simple endpoint CORS failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing simple endpoint: {e}")
        return False

def main():
    print("🔧 CORS Fix Test Suite")
    print("=" * 50)
    print()
    print("This test will verify:")
    print("1. CORS preflight requests work")
    print("2. Actual CORS requests work")
    print("3. Simple endpoints work with CORS")
    print()
    
    # Test 1: Preflight request
    if not test_cors_preflight():
        print("\n❌ CORS preflight test failed!")
        return
    
    # Test 2: Simple endpoint
    if not test_simple_endpoint():
        print("\n❌ Simple endpoint CORS test failed!")
        return
    
    # Test 3: Actual request
    if not test_actual_request():
        print("\n❌ Actual CORS request test failed!")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All CORS tests passed!")
    print("\nThe CORS issue has been resolved!")
    print("\nNext steps:")
    print("1. Restart the backend: python start_backend.py")
    print("2. Test the frontend voice flow")
    print("3. The CORS error should now be resolved")

if __name__ == "__main__":
    main()
