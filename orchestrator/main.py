"""FastAPI orchestrator"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from .models import BuildRequest
from ..agents.manager import generate_manager_output
from ..agents.backend import generate_backend_code
from ..agents.frontend import generate_frontend_code
from ..codegen.writer import project_writer
from ..codegen.validators import spec_validator

app = FastAPI(title="Kitchen Orchestrator")


@app.post("/build")
async def build(request: BuildRequest):
    """Build complete project from user prompt using AI agents and templates"""
    try:
        # Step 1: Generate manager output with backend and frontend prompts
        manager_output = await generate_manager_output(request.user_prompt)

        # Step 2: Generate backend specifications using AI
        backend_specs = await generate_backend_code(
            manager_output.backend_engineer_prompt,
            manager_output.frontend_engineer_prompt
        )

        # Step 3: Generate frontend specifications using AI
        frontend_specs = await generate_frontend_code(
            manager_output.frontend_engineer_prompt,
            backend_specs["entities"]
        )

        # Step 4: Validate project specifications
        project_data = {
            "project_name": extract_project_name(manager_output.backend_engineer_prompt.project_context),
            "entities": backend_specs["entities"],
            "pages": frontend_specs["pages"],
            "components": frontend_specs["components"]
        }

        validated_spec = spec_validator.validate_project_spec(project_data)

        # Step 5: Generate complete project using templates
        project_path = project_writer.generate_project(validated_spec.dict())

        # Step 6: Create ZIP archive
        zip_path = project_writer.create_zip_archive(project_path)

        return {
            "status": "complete",
            "project_path": project_path,
            "zip_file": zip_path,
            "specifications": {
                "entities": validated_spec.entities,
                "pages": frontend_specs["pages"],
                "components": frontend_specs["components"]
            },
            "prompts": {
                "backend": manager_output.backend_engineer_prompt.dict(),
                "frontend": manager_output.frontend_engineer_prompt.dict()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Build failed: {str(e)}")


@app.get("/download/{project_name}")
async def download_project(project_name: str):
    """Download generated project as ZIP file"""
    zip_path = f"{project_name}.zip"
    return FileResponse(
        path=zip_path,
        filename=f"{project_name}.zip",
        media_type="application/zip"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Kitchen Orchestrator"}


def extract_project_name(project_context: str) -> str:
    """Extract project name from context"""
    # Simple extraction - look for common patterns
    words = project_context.split()
    for i, word in enumerate(words):
        if word.lower() in ['build', 'create', 'develop', 'make'] and i + 1 < len(words):
            next_word = words[i + 1]
            if next_word[0].isupper():
                return next_word

    # Default fallback
    return "GeneratedProject"