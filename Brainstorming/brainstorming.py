import os
import io
import time
import queue
import numpy as np
import tempfile
import sounddevice as sd
import soundfile as sf
import simpleaudio as sa
from dotenv import load_dotenv

# --- Google Cloud ---
from google.cloud import speech
from google.cloud import texttospeech
import google.generativeai as genai

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
    while True:
        ans = listen_once(q + " Please say yes or no.").lower()

        if any(word in ans for word in ["yes", "yeah", "yep", "sure", "correct"]):
            return True
        elif any(word in ans for word in ["no", "nope", "nah"]):
            return False
        else:
            speak("I'm sorry, I didn't understand. Please say yes or no.")
            print("[System]: No valid response. Asking user to repeat.")


def choose_from_list(q: str, options: list, allow_none=False, regenerate_func=None) -> str:
    first_time = True
    while True:  # loop until a valid match
        # Add "None of the above" if enabled
        display_options = options[:]
        if allow_none:
            display_options = options + ["None of the above"]

        if first_time:
            speak(q)
            print(f"[System]: {q}")
            for i, opt in enumerate(display_options, 1):
                msg = f"Option {i}: {opt}"
                speak(msg)
                print(msg)
            ans = listen_once(f"Please say option 1 through option {len(display_options)}.").lower()
            first_time = False
        else:
            speak("Could you repeat again? Please say one of the options.")
            print("[System]: Asking user to repeat.")
            ans = listen_once().lower()

        # Match option numbers
        for i, opt in enumerate(display_options, 1):
            if f"option {i}" in ans or ans.strip() == str(i) or f"number {i}" in ans:
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
    has_idea = ask_yes_no("Do you already have a website idea?")
    if has_idea:
        idea = listen_once("Great! Please describe your idea.", max_record_sec=20)
        speak("Your chosen website idea is: " + idea)
        
        return

    category = choose_from_list("Choose a category:", CATEGORIES)

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




# ---------- Entry ----------
if __name__ == "__main__":
    brainstorm_session()
