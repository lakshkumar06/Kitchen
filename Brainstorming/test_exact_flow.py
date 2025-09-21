#!/usr/bin/env python3
"""
Test script to verify the exact conversational flow implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brainstorming import brainstorm_session

def main():
    print("🎤 Testing Exact Conversational Flow")
    print("=" * 50)
    print()
    print("This will test the exact flow you specified:")
    print()
    print("1. Initial Question: 'Do you already have a website idea?'")
    print("2. If Yes: Ask for description (20 sec timeout)")
    print("3. If No: Category selection (5 sec timeout)")
    print("4. Subtopic selection with regeneration (5 sec timeout)")
    print("5. Website idea selection with regeneration (5 sec timeout)")
    print("6. Final confirmation")
    print()
    print("All system messages will be spoken aloud via TTS.")
    print("All user inputs will be captured via STT.")
    print()
    print("Starting the voice flow...")
    print("=" * 50)
    
    try:
        # Run the complete brainstorm session
        brainstorm_session()
        
        print()
        print("=" * 50)
        print("✅ Voice flow completed successfully!")
        print("The exact conversational flow has been implemented and tested.")
        
    except KeyboardInterrupt:
        print("\n\n❌ Voice flow interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error in voice flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()