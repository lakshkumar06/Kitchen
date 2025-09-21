#!/usr/bin/env python3
"""
Complete integration test for the exact conversational flow
"""

import requests
import json
import time

BASE_URL = "http://localhost:5121"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Backend is running")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        print("   Start it with: python start_backend.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_complete_voice_flow():
    """Test the complete voice flow endpoint"""
    print("\n🎤 Testing Complete Voice Flow API")
    print("=" * 40)
    
    try:
        print("Calling /api/complete-voice-flow...")
        response = requests.post(f"{BASE_URL}/api/complete-voice-flow", 
                               json={},
                               timeout=30)  # Longer timeout for voice flow
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Complete voice flow API working!")
            print(f"Response: {data}")
            return True
        else:
            print(f"❌ Complete voice flow failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Voice flow may be taking too long.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_individual_endpoints():
    """Test individual endpoints to ensure they work"""
    print("\n🔧 Testing Individual Endpoints")
    print("=" * 40)
    
    endpoints = [
        ("/api/speak", {"text": "Hello, this is a test."}),
        ("/api/get-categories", {}),
    ]
    
    for endpoint, data in endpoints:
        try:
            if endpoint == "/api/speak":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            else:
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {endpoint} working")
            else:
                print(f"❌ {endpoint} failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")
            return False
    
    return True

def main():
    print("🎤 Complete Integration Test")
    print("=" * 50)
    print()
    print("This test will verify:")
    print("1. Backend is running")
    print("2. Individual endpoints work")
    print("3. Complete voice flow API works")
    print()
    
    # Test 1: Backend health
    if not test_backend_health():
        return
    
    # Test 2: Individual endpoints
    if not test_individual_endpoints():
        print("\n❌ Individual endpoint tests failed!")
        return
    
    # Test 3: Complete voice flow
    if test_complete_voice_flow():
        print("\n🎉 All tests passed!")
        print("\nThe exact conversational flow is ready to use!")
        print("\nNext steps:")
        print("1. Start the frontend: cd ../frontend && npm run dev")
        print("2. Click '🎤 Start Complete Voice Flow'")
        print("3. Follow the voice prompts in the backend console")
        print("\nExpected flow:")
        print("- System asks: 'Do you already have a website idea?'")
        print("- If Yes: Asks for description (20 sec timeout)")
        print("- If No: Category → Subtopic → Website idea selection")
        print("- All with proper error handling and regeneration")
    else:
        print("\n❌ Complete voice flow test failed!")
        print("Check the backend console for error details.")

if __name__ == "__main__":
    main()
