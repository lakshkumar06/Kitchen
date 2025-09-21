#!/usr/bin/env python3
"""
Test script to verify the audio fix is working
"""

import requests
import json
import time

BASE_URL = "http://localhost:5121"

def test_audio_endpoints():
    """Test the audio endpoints to ensure they work properly"""
    print("🔊 Testing Audio Endpoints")
    print("=" * 40)
    
    # Test 1: Text-to-Speech
    print("\n1️⃣ Testing text-to-speech...")
    try:
        response = requests.post(f"{BASE_URL}/api/speak", 
                               json={"text": "Hello, this is a test of the text to speech system."})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Text-to-speech successful")
            print(f"   Text: {data['text']}")
            print(f"   Audio data length: {len(data['audio'])} characters")
        else:
            print(f"❌ Text-to-speech failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Yes/No Question (this will speak and listen)
    print("\n2️⃣ Testing yes/no question...")
    print("   This will speak a question and wait for your response.")
    print("   Say 'yes' or 'no' when prompted.")
    
    try:
        response = requests.post(f"{BASE_URL}/api/ask-yes-no", 
                               json={"question": "Do you like testing?"})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Yes/no question successful")
            print(f"   Question: {data['question']}")
            print(f"   Your response: {data['response']}")
            print(f"   Interpreted as: {data['is_yes']}")
        else:
            print(f"❌ Yes/no question failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Description Question
    print("\n3️⃣ Testing description question...")
    print("   This will ask for a description and wait for your response.")
    
    try:
        response = requests.post(f"{BASE_URL}/api/ask-description", 
                               json={"question": "Please describe your favorite color.", "max_seconds": 10})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Description question successful")
            print(f"   Question: {data['question']}")
            print(f"   Your response: {data['response']}")
        else:
            print(f"❌ Description question failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Choice Question
    print("\n4️⃣ Testing choice question...")
    print("   This will ask you to choose from options.")
    
    try:
        response = requests.post(f"{BASE_URL}/api/ask-choice", 
                               json={
                                   "question": "What is your favorite fruit?",
                                   "options": ["Apple", "Banana", "Orange", "Grape"],
                                   "allow_none": False
                               })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Choice question successful")
            print(f"   Question: {data.get('question', 'N/A')}")
            print(f"   Your response: {data['response']}")
            print(f"   Chosen option: {data['chosen_option']}")
            print(f"   Is valid: {data['is_valid']}")
        else:
            print(f"❌ Choice question failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 All audio tests completed!")
    print("\nIf you heard the system speaking and were able to respond:")
    print("✅ Audio system is working correctly!")
    print("\nIf you didn't hear anything:")
    print("❌ Check your audio settings and backend configuration")
    
    return True

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

def main():
    print("🔊 Audio Fix Test Suite")
    print("=" * 40)
    
    # Check if backend is running
    if not test_backend_health():
        return
    
    # Run audio tests
    if test_audio_endpoints():
        print("\n🎯 Audio fix test completed successfully!")
        print("\nNext steps:")
        print("1. Start the frontend: cd ../frontend && npm run dev")
        print("2. Click '🎤 Start Complete Voice Flow'")
        print("3. Test the complete voice conversation")
    else:
        print("\n❌ Audio fix test failed!")

if __name__ == "__main__":
    main()
