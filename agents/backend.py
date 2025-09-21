"""Backend agent: generates code from backend prompt"""

import os
from ..orchestrator.models import BackendPrompt


async def generate_backend(backend_prompt: BackendPrompt) -> None:
    """Generate backend code from backend prompt"""
    os.makedirs("output/backend", exist_ok=True)

    # Generate FastAPI main app
    main_code = f'''"""
{backend_prompt.role}
{backend_prompt.domain_description}

Project Context: {backend_prompt.project_context}
Technologies: {backend_prompt.required_technologies}
"""
from fastapi import FastAPI

app = FastAPI(title="Backend API")

@app.get("/")
def read_root():
    return {{"message": "Backend API is running"}}

@app.get("/health")
def health_check():
    return {{"status": "healthy"}}
'''

    # Generate SQLAlchemy models
    models_code = f'''"""
SQLAlchemy Models
Generated according to: {backend_prompt.core_deliverables}
"""
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

# Add your models here following the project requirements
'''

    # Write files
    with open("output/backend/main.py", "w") as f:
        f.write(main_code)
    with open("output/backend/models.py", "w") as f:
        f.write(models_code)