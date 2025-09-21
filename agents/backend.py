"""Backend agent: generates code from backend prompt"""

import os
from orchestrator.models import BackendPrompt


async def generate_backend_code(backend_prompt: BackendPrompt) -> dict:
    """Generate backend code from backend prompt using LLM"""
    os.makedirs("output/backend", exist_ok=True)
    
    from providers.gemini import gemini_client
    
    # Create a comprehensive prompt for the LLM to generate the backend code
    llm_prompt = f"""
    You are a Backend Engineer. Generate complete, functional Python backend code based on the following requirements:

    Role: {backend_prompt.role}
    Domain Description: {backend_prompt.domain_description}
    Project Context: {backend_prompt.project_context}
    
    Required Technologies:
    - Programming Language: {backend_prompt.required_technologies.get('programming_language', 'Python')}
    - Web Framework: {backend_prompt.required_technologies.get('web_framework', 'FastAPI')}
    - Data Processing: {backend_prompt.required_technologies.get('data_processing', 'PySpark')}
    - Database ORM: {backend_prompt.required_technologies.get('database_orm', 'SQLAlchemy')}
    - Dependency Management: {backend_prompt.required_technologies.get('dependency_management', 'Python Poetry')}
    
    Code Requirements: {', '.join(backend_prompt.code_requirements)}
    Core Deliverables: {', '.join(backend_prompt.core_deliverables)}
    Integration Requirements: {', '.join(backend_prompt.integration_requirements)}
    Constraints: {', '.join(backend_prompt.constraints)}
    
    Generate complete, functional Python backend code that includes:
    1. A main.py file with FastAPI application setup
    2. A models.py file with SQLAlchemy models
    3. All necessary imports and dependencies
    4. Proper API endpoints and business logic
    5. Database models and relationships
    6. The code should be immediately executable
    7. Include proper error handling and validation
    
    Return the code in the following format:
    === MAIN.PY ===
    [main.py code here]
    
    === MODELS.PY ===
    [models.py code here]
    
    Return ONLY the code, nothing else.
    """
    
    # Generate the backend code using the LLM
    backend_code = gemini_client.generate(llm_prompt)
    
    # Parse the response to extract main.py and models.py
    if "=== MAIN.PY ===" in backend_code and "=== MODELS.PY ===" in backend_code:
        parts = backend_code.split("=== MAIN.PY ===")[1].split("=== MODELS.PY ===")
        main_code = parts[0].strip()
        models_code = parts[1].strip()
    else:
        # Fallback: treat the entire response as main.py
        main_code = backend_code
        models_code = f'''"""
SQLAlchemy Models
Generated according to: {', '.join(backend_prompt.core_deliverables)}
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
    
    return {
        "success": True,
        "main_file": "output/backend/main.py",
        "models_file": "output/backend/models.py",
        "main_code": main_code,
        "models_code": models_code
    }