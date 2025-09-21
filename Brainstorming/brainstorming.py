import os
import io
import time
import queue
import numpy as np
import tempfile
import sounddevice as sd
import soundfile as sf
import simpleaudio as sa
import sys
import asyncio
from dotenv import load_dotenv

# --- Google Cloud ---
from google.cloud import speech
from google.cloud import texttospeech
import google.generativeai as genai

# --- Import manager for coding flow ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents.manager import generate_manager_output

# ------------- Setup -------------
load_dotenv()


# Gemini API
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise RuntimeError("Set GEMINI_API_KEY in .env")
genai.configure(api_key=gemini_key)

# Create Google Cloud clients
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

# Audio constants
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'
CHUNK_SEC = 0.2
MAX_RECORD_SEC = 12
SILENCE_HANG = 0.8

# ---------- Utils: TTS ----------
def speak(text: str, voice_name="en-US-Neural2-C"):
    """Convert text to speech with Google Cloud and play it back safely on Windows."""
    if not text:
        return

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save to a temporary wav file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(response.audio_content)
        tmp_path = f.name

    # Play with sounddevice (more stable than simpleaudio on Windows)
    data, fs = sf.read(tmp_path, dtype='int16')
    sd.play(data, fs)
    sd.wait()

# ---------- Utils: STT ----------
def listen_once(prompt=None, max_record_sec=5) -> str:
    """Record one response and transcribe."""
    if prompt:
        print(f"\n[System]: {prompt}")
        speak(prompt)
        time.sleep(0.3)

    print(f"[System]: Listening (timeout {max_record_sec} sec)...")
    frames = []
    silence_start = None
    start_time = time.time()
    chunk_samples = int(SAMPLE_RATE * CHUNK_SEC)

    def callback(indata, frames_count, time_info, status):
        audio_q.put(indata.copy())

    audio_q = queue.Queue()
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, callback=callback):
        while True:
            chunk = audio_q.get()
            frames.append(chunk)
            rms = np.sqrt(np.mean(np.square(chunk.astype(np.float32))))
            speaking = rms > 200
            now = time.time()
            if speaking:
                silence_start = None
            else:
                if silence_start is None:
                    silence_start = now
                elif (now - silence_start) >= SILENCE_HANG and (now - start_time) > 1.0:
                    break
            if (now - start_time) >= max_record_sec:
                break

    audio = np.concatenate(frames, axis=0)
    wav_buf = io.BytesIO()
    sf.write(wav_buf, audio, SAMPLE_RATE, format='WAV', subtype='PCM_16')
    wav_buf.seek(0)

    audio_g = speech.RecognitionAudio(content=wav_buf.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="en-US",
        enable_automatic_punctuation=True
    )
    resp = speech_client.recognize(config=config, audio=audio_g)
    if resp.results:
        transcript = resp.results[0].alternatives[0].transcript.strip()
        print(f"[You]: {transcript}")
        return transcript
    else:
        return ""


# ---------- Utils: Gemini ----------
def gemini_list_items(prompt: str, n=3, exclude=None) -> list:
    """Get n short unique items from Gemini, avoiding exclude list."""
    if exclude is None:
        exclude = []

    model = genai.GenerativeModel("gemini-1.5-flash")
    sys_prompt = (
        "Return exactly the requested number of short items.\n"
        "Number them 1..N. Keep each under 12 words.\n"
        "No extra commentary."
    )

    # Add exclusion note to prompt
    exclude_text = ""
    if exclude:
        exclude_text = " Avoid repeating any of these: " + "; ".join(exclude)

    r = model.generate_content(f"{sys_prompt}\n\nTask: {prompt}{exclude_text}\nReturn {n} items.")
    lines = [ln.strip("-• ").strip() for ln in r.text.strip().splitlines() if ln.strip()]

    items = []
    for ln in lines:
        if ln[0].isdigit():
            ln = ln.split(".", 1)[-1].strip() if "." in ln[:3] else ln
        items.append(ln)

    # Deduplicate against history
    unique_items = [it for it in items if it not in exclude]

    return unique_items[:n]


# ---------- Flow ----------
CATEGORIES = ["Healthcare", "Art", "Education", "E-commerce"]

def ask_yes_no(q: str) -> bool:
    """Ask yes/no question with exact flow specification"""
    while True:
        # Speak the question
        speak(q)
        print(f"[System]: {q}")
        
        # Show listening message
        print("[System]: Listening (timeout 5 sec)...")
        
        # Listen for response
        ans = listen_once("", max_record_sec=5).lower()

        if any(word in ans for word in ["yes", "yeah", "yep", "sure", "correct"]):
            return True
        elif any(word in ans for word in ["no", "nope", "nah"]):
            return False
        else:
            print("[System]: No valid response. Asking user to repeat.")
            # Loop continues and asks the question again


def choose_from_list(q: str, options: list, allow_none=False, regenerate_func=None) -> str:
    """Choose from list with exact flow specification"""
    first_time = True
    while True:  # loop until a valid match
        # Add "None of the above" if enabled
        display_options = options[:]
        if allow_none:
            display_options = options + ["None of the above"]

        if first_time:
            # Speak the question
            speak(q)
            print(f"[System]: {q}")
            
            # Speak all options
            for i, opt in enumerate(display_options, 1):
                msg = f"Option {i}: {opt}"
                speak(msg)
                print(msg)
            
            # Ask for choice
            speak(f"Please say option 1 through option {len(display_options)}.")
            print(f"[System]: Please say option 1 through option {len(display_options)}.")
            
            # Show listening message
            print("[System]: Listening (timeout 5 sec)...")
            
            # Listen for response
            ans = listen_once("", max_record_sec=5).lower()
            first_time = False
        else:
            print("[System]: Asking user to repeat.")
            speak("Could you repeat again? Please say one of the options.")
            print("[System]: Listening (timeout 5 sec)...")
            ans = listen_once("", max_record_sec=5).lower()

        # Match option numbers - require "Option X" format
        for i, opt in enumerate(display_options, 1):
            if f"option {i}" in ans or ans.strip().lower() == f"option {i}":
                chosen_opt = opt
                if allow_none and chosen_opt.lower().startswith("none"):
                    if regenerate_func:
                        # regenerate new ideas/subtopics and restart loop
                        new_options = regenerate_func()
                        options[:] = new_options  # replace contents
                        first_time = True
                        break
                return chosen_opt

        # Keyword fallback
        for opt in display_options:
            if opt.lower() in ans:
                if allow_none and "none" in opt.lower():
                    if regenerate_func:
                        new_options = regenerate_func()
                        options[:] = new_options
                        first_time = True
                        break
                return opt





def brainstorm_session():
    """Complete brainstorming session with exact flow specification"""
    
    # Step 1: Initial Question
    has_idea = ask_yes_no("Do you already have a website idea?")
    
    if has_idea:
        # Case B: User says "Yes"
        speak("Great! Please describe your idea in detail. Include what features you want, who your target users are, and any specific functionality you need.")
        print("[System]: Great! Please describe your idea in detail. Include what features you want, who your target users are, and any specific functionality you need.")
        print("[System]: Listening (timeout 30 sec)...")
        
        idea = listen_once("", max_record_sec=30)
        print(f"[You]: {idea}")
        
        # Enhanced prompt to capture more details
        speak("Let me gather a bit more information. What type of website is this - a simple tool, a business platform, or something that needs user accounts and data storage?")
        print("[System]: Let me gather a bit more information. What type of website is this - a simple tool, a business platform, or something that needs user accounts and data storage?")
        website_type = listen_once("", max_record_sec=15)
        print(f"[You]: {website_type}")
        
        # Combine the information for better context
        full_idea = f"{idea}. Website type: {website_type}"
        
        speak("Perfect! Now I'll start coding your website. This may take a moment.")
        print("[System]: Perfect! Now I'll start coding your website. This may take a moment.")
        
        # Trigger the programming flow
        trigger_coding_flow(full_idea)
        return

    # Case C: User says "No" - Move to category selection
    # Use fixed categories list
    category = choose_from_list("Choose a category:", CATEGORIES)

    # Track used subtopics for regeneration
    used_subtopics = []
    def regen_subtopics():
        new_items = gemini_list_items(
            f"Generate 3 creative subtopics for {category}",
            3,
            exclude=used_subtopics
        )
        used_subtopics.extend(new_items)
        return new_items

    # Subtopic Selection with regeneration support
    subtopics = regen_subtopics()
    subtopic = choose_from_list("Choose a subtopic:", subtopics, allow_none=True, regenerate_func=regen_subtopics)

    # Track used ideas for regeneration
    used_ideas = []
    def regen_ideas():
        new_items = gemini_list_items(
            f"Generate 3 website ideas for {subtopic} in {category}",
            3,
            exclude=used_ideas
        )
        used_ideas.extend(new_items)
        return new_items

    # Website Idea Selection with regeneration support
    ideas = regen_ideas()
    chosen = choose_from_list("Choose a website idea:", ideas, allow_none=True, regenerate_func=regen_ideas)

    # Final Confirmation
    print("\n=== RESULT ===")
    print(f"Category: {category}")
    print(f"Subtopic: {subtopic}")
    print(f"Website idea: {chosen}")
    speak("Your chosen website idea is: " + chosen)
    print(f"[System]: Your chosen website idea is: {chosen}")
    
    # Enhanced prompt to capture more details
    speak("Let me gather a bit more information. What type of website is this - a simple tool, a business platform, or something that needs user accounts and data storage?")
    print("[System]: Let me gather a bit more information. What type of website is this - a simple tool, a business platform, or something that needs user accounts and data storage?")
    website_type = listen_once("", max_record_sec=15)
    print(f"[You]: {website_type}")
    
    # Combine the information for better context
    full_idea = f"{chosen}. Category: {category}, Subtopic: {subtopic}. Website type: {website_type}"
    
    speak("Perfect! Now I'll start coding your website. This may take a moment.")
    print("[System]: Perfect! Now I'll start coding your website. This may take a moment.")
    
    # Trigger the programming flow
    trigger_coding_flow(full_idea)


def brainstorm_with_idea(idea_description):
    """Handle brainstorming when user already has an idea"""
    speak("Great! Please describe your idea in detail. Include what features you want, who your target users are, and any specific functionality you need.")
    print("[System]: Great! Please describe your idea in detail. Include what features you want, who your target users are, and any specific functionality you need.")
    idea = listen_once("", max_record_sec=30)
    print(f"[You]: {idea}")
    
    # Enhanced prompt to capture more details
    speak("Let me gather a bit more information. What type of website is this - a simple tool, a business platform, or something that needs user accounts and data storage?")
    print("[System]: Let me gather a bit more information. What type of website is this - a simple tool, a business platform, or something that needs user accounts and data storage?")
    website_type = listen_once("", max_record_sec=15)
    print(f"[You]: {website_type}")
    
    # Combine the information for better context
    full_idea = f"{idea}. Website type: {website_type}"
    
    speak("Perfect! Now I'll start coding your website. This may take a moment.")
    print("[System]: Perfect! Now I'll start coding your website. This may take a moment.")
    
    # Trigger the programming flow
    trigger_coding_flow(full_idea)
    
    return {
        "idea": full_idea,
        "type": "user_provided",
        "coding_triggered": True
    }


def brainstorm_without_idea():
    """Handle brainstorming when user needs help finding an idea"""
    # Generate dynamic categories using Gemini
    categories = gemini_list_items("Generate 4 diverse business categories for website ideas", 4)
    
    category = choose_from_list("Choose a category:", categories)

    # Track used subtopics
    used_subtopics = []
    def regen_subtopics():
        new_items = gemini_list_items(
            f"Generate 3 creative subtopics for {category}",
            3,
            exclude=used_subtopics
        )
        used_subtopics.extend(new_items)
        return new_items

    subtopics = regen_subtopics()
    subtopic = choose_from_list("Choose a subtopic:", subtopics, allow_none=True, regenerate_func=regen_subtopics)

    # Track used ideas
    used_ideas = []
    def regen_ideas():
        new_items = gemini_list_items(
            f"Generate 3 website ideas for {subtopic} in {category}",
            3,
            exclude=used_ideas
        )
        used_ideas.extend(new_items)
        return new_items

    ideas = regen_ideas()
    chosen = choose_from_list("Choose a website idea:", ideas, allow_none=True, regenerate_func=regen_ideas)

    print("\n=== RESULT ===")
    print(f"Category: {category}")
    print(f"Subtopic: {subtopic}")
    print(f"Website idea: {chosen}")
    speak("Your chosen website idea is: " + chosen)
    print(f"[System]: Your chosen website idea is: {chosen}")
    
    return {
        "idea": chosen,
        "category": category,
        "subtopic": subtopic,
        "type": "generated"
    }


def get_dynamic_categories():
    """Get dynamic categories for frontend display"""
    return gemini_list_items("Generate 4 diverse business categories for website ideas", 4)


def get_dynamic_subtopics(category):
    """Get dynamic subtopics for a given category"""
    return gemini_list_items(f"Generate 3 creative subtopics for {category}", 3)


def get_dynamic_ideas(category, subtopic):
    """Get dynamic website ideas for a given category and subtopic"""
    return gemini_list_items(f"Generate 3 website ideas for {subtopic} in {category}", 3)


def create_basic_website(idea_description):
    """Create a basic website when API calls fail"""
    import os
    
    # Create output directory
    os.makedirs("output/frontend", exist_ok=True)
    
    # Extract key information from the idea
    idea_lower = idea_description.lower()
    
    # Determine website type and features
    if "task" in idea_lower or "todo" in idea_lower or "management" in idea_lower:
        title = "Task Manager"
        features = ["Add Tasks", "Mark Complete", "Delete Tasks", "Filter Tasks"]
        description = "A simple task management application"
    elif "calculator" in idea_lower:
        title = "Calculator"
        features = ["Basic Operations", "Clear Function", "Error Handling", "Responsive Design"]
        description = "A functional calculator application"
    elif "portfolio" in idea_lower or "personal" in idea_lower:
        title = "Personal Portfolio"
        features = ["About Section", "Skills Display", "Project Gallery", "Contact Form"]
        description = "A personal portfolio website"
    else:
        title = "My Website"
        features = ["Home Page", "About Section", "Contact Form", "Responsive Design"]
        description = "A custom website based on your idea"
    
    # Generate basic HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .feature {{
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .feature:hover {{
            transform: translateY(-5px);
        }}
        
        .feature h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .description {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .cta {{
            text-align: center;
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        
        .btn:hover {{
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p class="subtitle">Built with AI-powered development</p>
        </header>
        
        <div class="description">
            <h2>About This Website</h2>
            <p>{description}. This website was generated based on your idea: "{idea_description}".</p>
            <p>It features a modern, responsive design with clean code and user-friendly interface.</p>
        </div>
        
        <div class="features">
            {"".join([f'''
            <div class="feature">
                <h3>{feature}</h3>
                <p>Implemented with modern web technologies</p>
            </div>''' for feature in features])}
        </div>
        
        <div class="cta">
            <h3>Ready to Use!</h3>
            <p>Your website is fully functional and ready to deploy.</p>
            <button class="btn" onclick="alert('Website is ready! This is a basic version generated from your idea.')">
                Test Website
            </button>
        </div>
    </div>
    
    <script>
        // Basic functionality
        console.log('{title} loaded successfully!');
        
        // Add some interactive features
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Website initialized based on: {idea_description}');
        }});
    </script>
</body>
</html>'''
    
    # Write the file
    with open("output/frontend/index.html", "w") as f:
        f.write(html_content)
    
    return {
        "success": True,
        "file_path": "output/frontend/index.html",
        "title": title,
        "description": description
    }


def trigger_coding_flow(idea_description):
    """Trigger the coding flow using manager.py after brainstorming"""
    try:
        print("\n" + "="*60)
        print("🚀 STARTING CODING FLOW")
        print("="*60)
        
        # Create enhanced prompt for manager
        enhanced_prompt = f"""
        Create a complete website based on this idea: {idea_description}
        
        Requirements:
        - Build a fully functional website
        - Include all necessary features mentioned
        - Make it production-ready with clean, working code
        - Optimize for performance and user experience
        - Include proper error handling and validation
        """
        
        print(f"[Manager]: Analyzing requirements: {idea_description}")
        
        # Run the manager asynchronously
        async def run_manager():
            try:
                manager_output = await generate_manager_output(enhanced_prompt)
                print(f"[Manager]: Project type determined: {manager_output.project_type}")
                
                # Import and run the appropriate agents
                if manager_output.project_type == "frontend_only":
                    print("[Manager]: Starting Frontend Engineer...")
                    from agents.frontend import generate_frontend_code
                    frontend_result = await generate_frontend_code(manager_output.frontend_engineer_prompt)
                    print("[Manager]: Frontend development completed!")
                    return frontend_result
                else:
                    print("[Manager]: Starting Backend and Frontend Engineers...")
                    from agents.backend import generate_backend_code
                    from agents.frontend import generate_frontend_code
                    
                    # Run both in parallel
                    backend_task = generate_backend_code(manager_output.backend_engineer_prompt)
                    frontend_task = generate_frontend_code(manager_output.frontend_engineer_prompt)
                    
                    backend_result, frontend_result = await asyncio.gather(backend_task, frontend_task)
                    print("[Manager]: Full-stack development completed!")
                    return {"backend": backend_result, "frontend": frontend_result}
                    
            except Exception as e:
                print(f"[Manager Error]: {str(e)}")
                speak("I encountered an error while coding your website. Let me try a simpler approach.")
                print("[System]: Falling back to basic website generation...")
                
                # Create a basic website as fallback
                result = create_basic_website(idea_description)
                return result
        
        # Run the async function
        result = asyncio.run(run_manager())
        
        if result:
            speak("Your website has been created successfully! Check the output folder for the generated code.")
            print("[System]: Website creation completed! Check the output folder.")
            if isinstance(result, dict) and result.get("file_path"):
                print(f"[System]: Website saved to: {result['file_path']}")
        else:
            speak("I've created a basic version of your website. You can find it in the output folder.")
            print("[System]: Basic website created in output folder.")
            
    except Exception as e:
        print(f"[Coding Flow Error]: {str(e)}")
        speak("I encountered an issue while creating your website. Let me create a basic version.")
        print("[System]: Creating basic website as fallback...")
        
        # Final fallback
        result = create_basic_website(idea_description)
        if result:
            speak("I've created a basic version of your website. You can find it in the output folder.")
            print("[System]: Basic website created in output folder.")


# ---------- Entry ----------
if __name__ == "__main__":
    brainstorm_session()
