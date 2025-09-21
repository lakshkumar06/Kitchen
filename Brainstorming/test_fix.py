#!/usr/bin/env python3
"""
Test script to verify the 500 error fix
"""

import requests
import json

BASE_URL = "http://localhost:5121"

def test_complete_voice_flow():
    """Test the complete voice flow endpoint"""
    print("🔧 Testing Complete Voice Flow Fix")
    print("=" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/api/complete-voice-flow", 
                               json={})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Complete voice flow endpoint working!")
            print(f"Response: {data}")
            return True
        else:
            print(f"❌ Complete voice flow failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

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
    print("🔧 500 Error Fix Test")
    print("=" * 40)
    
    # Check if backend is running
    if not test_backend_health():
        return
    
    # Test the complete voice flow endpoint
    if test_complete_voice_flow():
        print("\n🎉 Fix successful!")
        print("The 500 Internal Server Error has been resolved.")
        print("\nNext steps:")
        print("1. Start the frontend: cd ../frontend && npm run dev")
        print("2. Click '🎤 Start Complete Voice Flow'")
        print("3. The voice conversation will run in the backend console")
    else:
        print("\n❌ Fix failed!")
        print("The 500 error is still occurring.")

if __name__ == "__main__":
    main()
