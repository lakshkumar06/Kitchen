"""Simplified brainstorming utilities for API use"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Gemini API Configuration
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=gemini_key)

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

    try:
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
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        # Return fallback items
        return [f"AI-Generated Idea {i+1}" for i in range(min(n, 3))]

def gemini_generate_text(prompt: str) -> str:
    """Generate a single text response from Gemini"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        return "AI-generated content unavailable"
