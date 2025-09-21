"""FastAPI orchestrator"""

from fastapi import FastAPI
from .models import BuildRequest
from ..agents.manager import generate_manager_output
from ..agents.backend import generate_backend
from ..agents.frontend import generate_frontend

app = FastAPI(title="Kitchen Orchestrator")


@app.post("/build")
async def build(request: BuildRequest):
    """Build project from user prompt using correct system prompt"""
    # Generate manager output with backend and frontend prompts
    manager_output = await generate_manager_output(request.user_prompt)

    # Generate code using the specific prompts
    await generate_backend(manager_output.backend_engineer_prompt)
    await generate_frontend(manager_output.frontend_engineer_prompt)

    return {
        "status": "complete",
        "backend_prompt": manager_output.backend_engineer_prompt.dict(),
        "frontend_prompt": manager_output.frontend_engineer_prompt.dict()
    }