"""Core models"""

from typing import Dict, List
from pydantic import BaseModel


class BackendPrompt(BaseModel):
    role: str
    domain_description: str
    project_context: str
    required_technologies: Dict[str, str]
    code_requirements: List[str]
    core_deliverables: List[str]
    integration_requirements: List[str]
    constraints: List[str]


class FrontendPrompt(BaseModel):
    role: str
    domain_description: str
    project_context: str
    required_technologies: Dict[str, str]
    code_requirements: List[str]
    core_deliverables: List[str]
    api_integration_requirements: List[str] = []
    constraints: List[str]


class ManagerOutput(BaseModel):
    project_type: str = "full_stack"  # "frontend_only" or "full_stack"
    backend_engineer_prompt: BackendPrompt = None
    frontend_engineer_prompt: FrontendPrompt


class BuildRequest(BaseModel):
    user_prompt: str