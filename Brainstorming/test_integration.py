#!/usr/bin/env python3
"""
Integration test script for the complete brainstorming flow
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_complete_flow():
    """Test the complete brainstorming flow"""
    print("🧪 Testing Complete Brainstorming Integration")
    print("=" * 50)
    
    # Test 1: Get dynamic categories
    print("\n1️⃣ Testing dynamic categories...")
    try:
        response = requests.get(f"{BASE_URL}/api/get-categories")
        if response.status_code == 200:
            data = response.json()
            categories = data['categories']
            print(f"✅ Got {len(categories)} dynamic categories:")
            for i, cat in enumerate(categories, 1):
                print(f"   {i}. {cat}")
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Get subtopics for first category
    if categories:
        print(f"\n2️⃣ Testing subtopics for '{categories[0]}'...")
        try:
            response = requests.post(f"{BASE_URL}/api/get-subtopics", 
                                   json={"category": categories[0]})
            if response.status_code == 200:
                data = response.json()
                subtopics = data['subtopics']
                print(f"✅ Got {len(subtopics)} subtopics:")
                for i, sub in enumerate(subtopics, 1):
                    print(f"   {i}. {sub}")
            else:
                print(f"❌ Failed to get subtopics: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Test 3: Get ideas for category and subtopic
    if categories and subtopics:
        print(f"\n3️⃣ Testing ideas for '{categories[0]}' + '{subtopics[0]}'...")
        try:
            response = requests.post(f"{BASE_URL}/api/get-ideas", 
                                   json={"category": categories[0], "subtopic": subtopics[0]})
            if response.status_code == 200:
                data = response.json()
                ideas = data['ideas']
                print(f"✅ Got {len(ideas)} ideas:")
                for i, idea in enumerate(ideas, 1):
                    print(f"   {i}. {idea['title']}")
                    print(f"      {idea['description']}")
            else:
                print(f"❌ Failed to get ideas: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Test 4: Process user idea
    print(f"\n4️⃣ Testing user idea processing...")
    try:
        test_idea = "A social media platform for pet owners to share photos and connect"
        response = requests.post(f"{BASE_URL}/api/process-idea", 
                               json={"idea": test_idea})
        if response.status_code == 200:
            data = response.json()
            result = data['result']
            print(f"✅ Processed user idea:")
            print(f"   Idea: {result['idea']}")
            print(f"   Type: {result['type']}")
        else:
            print(f"❌ Failed to process idea: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 5: Text-to-speech
    print(f"\n5️⃣ Testing text-to-speech...")
    try:
        response = requests.post(f"{BASE_URL}/api/speak", 
                               json={"text": "Hello, this is a test of the integration."})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text-to-speech successful")
            print(f"   Audio data length: {len(data['audio'])} characters")
        else:
            print(f"❌ Text-to-speech failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All integration tests passed!")
    print("\nThe complete flow is working:")
    print("1. ✅ Dynamic categories generation")
    print("2. ✅ Dynamic subtopics generation") 
    print("3. ✅ Dynamic ideas generation")
    print("4. ✅ User idea processing")
    print("5. ✅ Text-to-speech functionality")
    
    print("\n🚀 Ready for frontend integration!")
    print("Start the frontend and test the voice flow:")
    print("1. Click '🎤 Start Voice Chat'")
    print("2. Say 'yes' or 'no' to having an idea")
    print("3. Follow the voice prompts")
    
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
    print("🔧 Brainstorming Integration Test Suite")
    print("=" * 50)
    
    # Check if backend is running
    if not test_backend_health():
        return
    
    # Run complete flow test
    if test_complete_flow():
        print("\n🎯 Integration test completed successfully!")
    else:
        print("\n❌ Integration test failed!")

if __name__ == "__main__":
    main()
