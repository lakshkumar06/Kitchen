#!/usr/bin/env python3
"""
Startup script for the brainstorming backend API
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with the required variables.")
        print("Example .env file:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        return False
    
    print("✅ Environment variables loaded successfully")
    return True

def check_google_cloud():
    """Check if Google Cloud credentials are available"""
    try:
        from google.cloud import speech
        from google.cloud import texttospeech
        
        # Try to create clients to test credentials
        speech_client = speech.SpeechClient()
        tts_client = texttospeech.TextToSpeechClient()
        
        print("✅ Google Cloud credentials are valid")
        return True
    except Exception as e:
        print(f"❌ Google Cloud credentials error: {e}")
        print("\nPlease ensure you have:")
        print("1. Google Cloud SDK installed")
        print("2. Authenticated with: gcloud auth application-default login")
        print("3. Enabled Speech-to-Text and Text-to-Speech APIs")
        return False

def main():
    print("🚀 Starting Brainstorming Backend API...")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check Google Cloud
    if not check_google_cloud():
        sys.exit(1)
    
    print("\n🎯 Starting Flask server...")
    print("Backend will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    from app import app
    app.run(debug=True, port=5000, host='0.0.0.0')

if __name__ == "__main__":
    main()
