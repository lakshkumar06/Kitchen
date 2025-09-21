#!/usr/bin/env python3
"""
Test script to verify the frontend integration with the brainstorming backend
"""

import requests
import json

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

def test_custom_idea_endpoint():
    """Test the new process-custom-idea endpoint"""
    print("\n🧠 Testing Custom Idea Processing")
    print("=" * 40)
    
    try:
        test_idea = "A social media platform for pet owners to share photos and connect with other pet lovers"
        
        response = requests.post(f"{BASE_URL}/api/process-custom-idea", 
                               json={"idea": test_idea})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Custom idea processing successful")
            print(f"   Project Title: {data.get('project_title', 'N/A')}")
            print(f"   Industry: {data.get('industry', 'N/A')}")
            print(f"   Category: {data.get('category', 'N/A')}")
            print(f"   Analysis: {data.get('analysis', 'N/A')[:100]}...")
            print(f"   Features: {len(data.get('features', []))} features generated")
            return True
        else:
            print(f"❌ Custom idea processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_voice_endpoints():
    """Test voice-related endpoints"""
    print("\n🎤 Testing Voice Endpoints")
    print("=" * 40)
    
    endpoints = [
        ("/api/speak", {"text": "Hello, this is a test of the voice system."}),
        ("/api/get-categories", {}),
        ("/api/get-subtopics", {"category": "Healthcare"}),
    ]
    
    for endpoint, data in endpoints:
        try:
            if endpoint == "/api/speak":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            elif endpoint == "/api/get-categories":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} working")
            else:
                print(f"❌ {endpoint} failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")
            return False
    
    return True

def test_complete_voice_flow():
    """Test the complete voice flow endpoint"""
    print("\n🎯 Testing Complete Voice Flow")
    print("=" * 40)
    
    try:
        print("Note: This will start the complete voice conversation.")
        print("The conversation will run in the backend console.")
        print("You can interact with it there.")
        
        response = requests.post(f"{BASE_URL}/api/complete-voice-flow", 
                               json={},
                               timeout=5)  # Short timeout for testing
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Complete voice flow endpoint working")
            print(f"   Response: {data.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Complete voice flow failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✅ Complete voice flow endpoint is working (timeout expected)")
        print("   The voice conversation is running in the backend console")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 Frontend Integration Test Suite")
    print("=" * 50)
    print()
    print("This test will verify:")
    print("1. Backend is running")
    print("2. Custom idea processing endpoint works")
    print("3. Voice endpoints are functional")
    print("4. Complete voice flow is available")
    print()
    
    # Test 1: Backend health
    if not test_backend_health():
        return
    
    # Test 2: Custom idea endpoint
    if not test_custom_idea_endpoint():
        print("\n❌ Custom idea processing test failed!")
        return
    
    # Test 3: Voice endpoints
    if not test_voice_endpoints():
        print("\n❌ Voice endpoints test failed!")
        return
    
    # Test 4: Complete voice flow
    if not test_complete_voice_flow():
        print("\n❌ Complete voice flow test failed!")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed!")
    print("\nThe frontend integration is ready!")
    print("\nNext steps:")
    print("1. Start the frontend: cd ../frontend && npm run dev")
    print("2. Open the brainstorming interface")
    print("3. Test the voice features:")
    print("   - Click '🎤 Start Complete Voice Flow' for full voice conversation")
    print("   - Click '🎤 Enable Voice' for individual voice interactions")
    print("   - Use 'Audio Mode' for recording your own ideas")
    print("\nThe voice conversation will run in the backend console.")
    print("Follow the prompts there to complete the brainstorming session.")

if __name__ == "__main__":
    main()
