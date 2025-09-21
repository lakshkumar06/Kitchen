#!/usr/bin/env python3
"""
Test script to verify the exact voice flow implementation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_voice_flow():
    """Test the complete voice flow"""
    print("🎤 Testing Complete Voice Flow")
    print("=" * 50)
    
    try:
        from brainstorming import brainstorm_session
        
        print("Starting brainstorming session...")
        print("This will test the exact flow you specified:")
        print("1. Ask 'Do you already have a website idea?'")
        print("2. Handle invalid responses with repetition")
        print("3. Generate dynamic categories, subtopics, and ideas")
        print("4. Handle 'None of the above' regeneration")
        print("5. Speak final result")
        print("\nPress Ctrl+C to stop the test")
        print("=" * 50)
        
        # Run the brainstorming session
        brainstorm_session()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        return False
    
    print("\n✅ Voice flow test completed!")
    return True

def test_individual_functions():
    """Test individual functions"""
    print("\n🔧 Testing Individual Functions")
    print("=" * 30)
    
    try:
        from brainstorming import (
            ask_yes_no, choose_from_list, gemini_list_items,
            get_dynamic_categories, get_dynamic_subtopics, get_dynamic_ideas
        )
        
        # Test dynamic content generation
        print("1. Testing dynamic categories...")
        categories = get_dynamic_categories()
        print(f"   Generated {len(categories)} categories: {categories}")
        
        if categories:
            print("2. Testing dynamic subtopics...")
            subtopics = get_dynamic_subtopics(categories[0])
            print(f"   Generated {len(subtopics)} subtopics for '{categories[0]}': {subtopics}")
            
            if subtopics:
                print("3. Testing dynamic ideas...")
                ideas = get_dynamic_ideas(categories[0], subtopics[0])
                print(f"   Generated {len(ideas)} ideas for '{categories[0]}' + '{subtopics[0]}': {ideas}")
        
        print("✅ Individual function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing individual functions: {e}")
        return False

def main():
    print("🧪 Voice Flow Test Suite")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment")
        print("Please create a .env file with your Gemini API key")
        return
    
    print("✅ Environment variables loaded")
    
    # Test individual functions first
    if not test_individual_functions():
        return
    
    # Ask user if they want to run the full voice test
    print("\n" + "=" * 50)
    response = input("Do you want to run the full voice flow test? (y/n): ").lower()
    
    if response in ['y', 'yes']:
        test_voice_flow()
    else:
        print("Skipping full voice flow test")
    
    print("\n🎯 Test suite completed!")

if __name__ == "__main__":
    main()
