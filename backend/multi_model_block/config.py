"""Configuration for Google API connections"""

import os
from typing import Optional


class GoogleAPIConfig:
    """Configuration for Google APIs including Gemini"""

    def __init__(self):
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.google_project_id: Optional[str] = os.getenv("GOOGLE_PROJECT_ID")
        self.google_application_credentials: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        # Gemini API settings
        self.gemini_model: str = "gemini-1.5-pro"  # Default model
        self.gemini_temperature: float = 0.1  # Low temperature for consistent outputs
        self.gemini_max_tokens: int = 8192
        self.gemini_timeout: int = 30  # seconds

        # API endpoints
        self.gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"

    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True

    def get_gemini_headers(self) -> dict:
        """Get headers for Gemini API requests"""
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.gemini_api_key
        }


# Global configuration instance
google_config = GoogleAPIConfig()