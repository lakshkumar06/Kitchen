"""Models for the manager agent that generates a single JSON output with both engineer prompts"""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class UserInput(BaseModel):
    """Raw user input to be processed by the manager"""
    content: str = Field(..., description="Original user prompt")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str = Field(..., description="Session identifier")


class ManagerOutput(BaseModel):
    """Single JSON output from manager containing both engineer prompts"""
    backend_engineer_prompt: Dict[str, Any] = Field(
        ...,
        description="Complete backend engineer prompt with all required fields"
    )
    frontend_engineer_prompt: Dict[str, Any] = Field(
        ...,
        description="Complete frontend engineer prompt with all required fields"
    )
    session_id: str = Field(..., description="Session identifier")
    generated_at: datetime = Field(default_factory=datetime.now)

    def validate_structure(self) -> Dict[str, bool]:
        """Validate that output matches the required structure from system prompt"""
        backend_required = [
            "role", "domain_description", "project_context", "required_technologies",
            "code_requirements", "core_deliverables", "integration_requirements", "constraints"
        ]

        frontend_required = [
            "role", "domain_description", "project_context", "required_technologies",
            "code_requirements", "core_deliverables", "api_integration_requirements", "constraints"
        ]

        backend_valid = all(field in self.backend_engineer_prompt for field in backend_required)
        frontend_valid = all(field in self.frontend_engineer_prompt for field in frontend_required)

        return {
            "backend_valid": backend_valid,
            "frontend_valid": frontend_valid,
            "overall_valid": backend_valid and frontend_valid,
            "missing_backend_fields": [f for f in backend_required if f not in self.backend_engineer_prompt],
            "missing_frontend_fields": [f for f in frontend_required if f not in self.frontend_engineer_prompt]
        }

    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to the exact JSON format expected by the system"""
        return {
            "backend_engineer_prompt": self.backend_engineer_prompt,
            "frontend_engineer_prompt": self.frontend_engineer_prompt
        }