"""Gemini API client for the manager agent"""

import json
import requests
from typing import Dict, Any, Optional
from .config import google_config


class GeminiClient:
    """Client for interacting with Google's Gemini API"""

    def __init__(self):
        self.config = google_config
        self.config.validate_config()

    def generate_content(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate content using Gemini API

        Args:
            prompt: User prompt to process
            system_prompt: System prompt for instructions

        Returns:
            API response containing generated content
        """
        url = f"{self.config.gemini_base_url}/models/{self.config.gemini_model}:generateContent"

        # Prepare the request payload
        contents = []

        # Add system prompt if provided
        if system_prompt:
            contents.append({
                "role": "system",
                "parts": [{"text": system_prompt}]
            })

        # Add user prompt
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.config.gemini_temperature,
                "maxOutputTokens": self.config.gemini_max_tokens,
                "responseMimeType": "application/json"
            }
        }

        try:
            response = requests.post(
                url,
                headers=self.config.get_gemini_headers(),
                json=payload,
                timeout=self.config.gemini_timeout
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini API response: {str(e)}")

    def extract_content_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extract the generated content from Gemini API response

        Args:
            response: Raw API response

        Returns:
            Extracted content text
        """
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                raise Exception("No candidates in Gemini response")

            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            if not parts:
                raise Exception("No parts in Gemini response content")

            return parts[0].get("text", "")

        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to extract content from Gemini response: {str(e)}")

    def generate_manager_response(self, user_prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Generate manager response using Gemini API with the system prompt

        Args:
            user_prompt: User's input prompt
            system_prompt: Complete system prompt for the manager agent

        Returns:
            Parsed JSON response containing backend and frontend prompts
        """
        try:
            # Generate content using Gemini
            response = self.generate_content(user_prompt, system_prompt)

            # Extract the content
            content_text = self.extract_content_from_response(response)

            # Parse the JSON response
            try:
                parsed_content = json.loads(content_text)
                return parsed_content
            except json.JSONDecodeError as e:
                raise Exception(f"Gemini returned invalid JSON: {str(e)}")

        except Exception as e:
            raise Exception(f"Failed to generate manager response: {str(e)}")


# Global client instance
gemini_client = GeminiClient()