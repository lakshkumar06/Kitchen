#!/usr/bin/env python3
"""
Test script for the brainstorming backend API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5121"

def test_speak():
    """Test text-to-speech endpoint"""
    print("🎤 Testing text-to-speech...")
    
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
    except Exception as e:
        print(f"❌ Error: {e}")

def test_generate_ideas():
    """Test idea generation endpoint"""
    print("\n💡 Testing idea generation...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/generate-ideas", 
                               json={
                                   "niche": "healthcare",
                                   "subNiche": "clinical", 
                                   "area": "Patient Records",
                                   "industry": "Healthcare",
                                   "category": "Clinical"
                               })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Idea generation successful")
            print(f"   Generated {len(data['ideas'])} ideas:")
            for i, idea in enumerate(data['ideas'], 1):
                print(f"   {i}. {idea['title']}")
        else:
            print(f"❌ Idea generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test if backend is running"""
    print("🏥 Testing backend health...")
    
    try:
        # Try to connect to the base URL
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
    print("🧪 Brainstorming Backend Test Suite")
    print("=" * 40)
    
    # Test if backend is running
    if not test_health():
        return
    
    # Test text-to-speech
    test_speak()
    
    # Test idea generation
    test_generate_ideas()
    
    print("\n" + "=" * 40)
    print("🎯 Test completed!")
    print("\nTo test voice features:")
    print("1. Start the frontend: cd ../frontend && npm run dev")
    print("2. Click '🎤 Start Voice Chat' in the brainstorming interface")
    print("3. Allow microphone access when prompted")

if __name__ == "__main__":
    main()
