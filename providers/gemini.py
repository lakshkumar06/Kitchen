"""Gemini client"""

import requests
from .config import GEMINI_API_KEY


class GeminiClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

    def generate(self, prompt: str) -> str:
        """Generate content"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }

        response = requests.post(
            self.url,
            headers={"x-goog-api-key": self.api_key},
            json=payload
        )

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]


gemini_client = GeminiClient()