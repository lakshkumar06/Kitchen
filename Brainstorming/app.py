from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import tempfile
import base64
from brainstorming import (
    speak, listen_once, gemini_list_items, speech_client, tts_client,
    brainstorm_with_idea, brainstorm_without_idea, get_dynamic_categories,
    get_dynamic_subtopics, get_dynamic_ideas
)
from google.cloud import speech
from google.cloud import texttospeech
import google.generativeai as genai

app = Flask(__name__)

# Configure CORS with more permissive settings
CORS(app, 
     origins=['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173', 'http://127.0.0.1:3000'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)

# Audio constants
SAMPLE_RATE = 16000
CHANNELS = 1

# Comprehensive CORS headers for all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173', 'http://127.0.0.1:3000']:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

# Handle preflight requests for all API routes
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_preflight(path):
    response = app.response_class()
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Brainstorming backend is running',
        'cors_enabled': True
    })

@app.route('/api/speak', methods=['POST'])
def text_to_speech():
    """Convert text to speech and return audio data"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Use the existing speak function but capture the audio
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-C"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Return audio as base64 encoded data
        audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'text': text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transcribe', methods=['POST'])
def speech_to_text():
    """Convert audio to text"""
    try:
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Read audio data
        audio_content = audio_file.read()
        
        # Create recognition audio object
        audio_g = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-US",
            enable_automatic_punctuation=True
        )
        
        # Perform speech recognition
        resp = speech_client.recognize(config=config, audio=audio_g)
        
        if resp.results:
            transcript = resp.results[0].alternatives[0].transcript.strip()
            return jsonify({
                'success': True,
                'transcript': transcript
            })
        else:
            return jsonify({
                'success': True,
                'transcript': ''
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask-yes-no', methods=['POST'])
def ask_yes_no():
    """Ask a yes/no question and get voice response"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Speak the question first
        speak(question + " Please say yes or no.")
        print(f"[System]: {question} Please say yes or no.")
        
        # Use the existing listen_once function
        response = listen_once("", max_record_sec=5)
        
        # Determine if it's yes or no
        response_lower = response.lower()
        is_yes = any(word in response_lower for word in ["yes", "yeah", "yep", "sure", "correct"])
        is_no = any(word in response_lower for word in ["no", "nope", "nah"])
        
        if is_yes:
            result = True
        elif is_no:
            result = False
        else:
            result = None  # Unclear response
        
        return jsonify({
            'success': True,
            'response': response,
            'is_yes': result,
            'question': question
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask-description', methods=['POST'])
def ask_description():
    """Ask for a description and get voice response"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        max_seconds = data.get('max_seconds', 20)
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Speak the question first
        speak(question)
        print(f"[System]: {question}")
        
        # Use the existing listen_once function
        response = listen_once("", max_record_sec=max_seconds)
        
        return jsonify({
            'success': True,
            'response': response,
            'question': question
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-ideas', methods=['POST'])
def generate_ideas():
    """Generate ideas using Gemini AI"""
    try:
        data = request.get_json()
        niche = data.get('niche', '')
        sub_niche = data.get('subNiche', '')
        area = data.get('area', '')
        industry = data.get('industry', '')
        category = data.get('category', '')
        
        # Generate ideas using Gemini
        prompt = f"Generate 4 creative website ideas for {area} in {category} within {industry}. Each idea should be unique and innovative."
        ideas = gemini_list_items(prompt, n=4)
        
        # Format ideas for frontend
        formatted_ideas = []
        for i, idea in enumerate(ideas, 1):
            formatted_ideas.append({
                'id': i,
                'title': idea,
                'description': f"A {idea.lower()} solution that addresses key challenges in {area}.",
                'features': [
                    'Modern, intuitive user interface',
                    'Scalable cloud infrastructure',
                    'Advanced analytics and reporting',
                    'Mobile-responsive design',
                    'Integration capabilities'
                ]
            })
        
        return jsonify({
            'success': True,
            'ideas': formatted_ideas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-categories', methods=['GET'])
def get_categories():
    """Get dynamic categories for frontend"""
    try:
        categories = get_dynamic_categories()
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-subtopics', methods=['POST'])
def get_subtopics():
    """Get dynamic subtopics for a category"""
    try:
        data = request.get_json()
        category = data.get('category', '')
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
        
        subtopics = get_dynamic_subtopics(category)
        return jsonify({
            'success': True,
            'subtopics': subtopics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-ideas', methods=['POST'])
def get_ideas():
    """Get dynamic ideas for a category and subtopic"""
    try:
        data = request.get_json()
        category = data.get('category', '')
        subtopic = data.get('subtopic', '')
        
        if not category or not subtopic:
            return jsonify({'error': 'Category and subtopic are required'}), 400
        
        ideas = get_dynamic_ideas(category, subtopic)
        
        # Format ideas for frontend
        formatted_ideas = []
        for i, idea in enumerate(ideas, 1):
            formatted_ideas.append({
                'id': i,
                'title': idea,
                'description': f"A {idea.lower()} solution that addresses key challenges in {subtopic}.",
                'features': [
                    'Modern, intuitive user interface',
                    'Scalable cloud infrastructure',
                    'Advanced analytics and reporting',
                    'Mobile-responsive design',
                    'Integration capabilities'
                ]
            })
        
        return jsonify({
            'success': True,
            'ideas': formatted_ideas
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-idea', methods=['POST'])
def process_idea():
    """Process user's idea and return confirmation"""
    try:
        data = request.get_json()
        idea = data.get('idea', '')
        
        if not idea:
            return jsonify({'error': 'Idea is required'}), 400
        
        result = brainstorm_with_idea(idea)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-custom-idea', methods=['POST'])
def process_custom_idea():
    """Process custom user idea with AI analysis"""
    try:
        data = request.get_json()
        idea = data.get('idea', '')
        audio_blob = data.get('audioBlob', None)
        
        if not idea and not audio_blob:
            return jsonify({'error': 'Idea or audio is required'}), 400
        
        # Use Gemini to analyze and enhance the idea
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Analyze this website idea and provide a structured response:
        Idea: "{idea}"
        
        Please provide:
        1. A clear project title (max 8 words)
        2. The most relevant industry/category
        3. A specific subcategory
        4. A brief analysis of the idea's potential
        5. Key features that should be included
        
        Format your response as JSON with these fields:
        - project_title: string
        - industry: string  
        - category: string
        - analysis: string
        - features: array of strings
        """
        
        response = model.generate_content(prompt)
        
        # Try to parse the JSON response
        try:
            import json
            result = json.loads(response.text)
        except:
            # Fallback if JSON parsing fails
            result = {
                'project_title': idea[:50] + '...' if len(idea) > 50 else idea,
                'industry': 'Technology',
                'category': 'Web Application',
                'analysis': f"This is a {idea.lower()} solution that addresses user needs.",
                'features': [
                    'Modern user interface',
                    'Responsive design',
                    'User authentication',
                    'Data management',
                    'Analytics dashboard'
                ]
            }
        
        return jsonify({
            'success': True,
            'project_title': result.get('project_title', idea),
            'industry': result.get('industry', 'Technology'),
            'category': result.get('category', 'Web Application'),
            'analysis': result.get('analysis', f"Analysis of {idea}"),
            'features': result.get('features', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask-choice', methods=['POST'])
def ask_choice():
    """Ask user to choose from a list of options"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        options = data.get('options', [])
        allow_none = data.get('allow_none', False)
        
        if not question or not options:
            return jsonify({'error': 'Question and options are required'}), 400
        
        # Add "None of the above" if enabled
        display_options = options[:]
        if allow_none:
            display_options = options + ["None of the above"]
        
        # Speak the question
        speak(question)
        print(f"[System]: {question}")
        
        # Speak each option
        for i, opt in enumerate(display_options, 1):
            msg = f"Option {i}: {opt}"
            speak(msg)
            print(msg)
        
        # Ask for choice
        speak(f"Please say option 1 through option {len(display_options)}.")
        print(f"[System]: Please say option 1 through option {len(display_options)}.")
        
        # Get response
        response = listen_once("", max_record_sec=5)
        print(f"[You]: {response}")
        
        # Parse response
        response_lower = response.lower()
        chosen_option = None
        
        # Check for option numbers
        for i, opt in enumerate(display_options, 1):
            if f"option {i}" in response_lower or response_lower.strip() == str(i) or f"number {i}" in response_lower:
                chosen_option = opt
                break
        
        # Check for keyword matches
        if not chosen_option:
            for opt in display_options:
                if opt.lower() in response_lower:
                    chosen_option = opt
                    break
        
        return jsonify({
            'success': True,
            'response': response,
            'chosen_option': chosen_option,
            'is_valid': chosen_option is not None,
            'is_none': chosen_option and chosen_option.lower().startswith("none") if chosen_option else False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask-repeat', methods=['POST'])
def ask_repeat():
    """Ask user to repeat their choice"""
    try:
        speak("Could you repeat again? Please say one of the options.")
        print("[System]: Asking user to repeat.")
        
        response = listen_once("", max_record_sec=5)
        print(f"[You]: {response}")
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete-voice-flow', methods=['POST'])
def complete_voice_flow():
    """Complete voice flow exactly as specified"""
    try:
        # Import the brainstorm_session function from brainstorming.py
        from brainstorming import brainstorm_session
        
        # Run the complete brainstorm session
        # This will handle the entire flow as specified
        brainstorm_session()
        
        # Since brainstorm_session doesn't return data, we'll return a success message
        return jsonify({
            'success': True,
            'flow_complete': True,
            'message': 'Voice flow completed successfully. Check console for results.'
        })
            
    except Exception as e:
        print(f"Error in complete voice flow: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5121)
