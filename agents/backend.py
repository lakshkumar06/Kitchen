"""Backend agent: generates code from backend prompt"""

from ..orchestrator.models import BackendPrompt
from ..providers.gemini import backend_client
from ..codegen.validators import spec_validator


async def generate_backend_code(backend_prompt: BackendPrompt, frontend_prompt) -> dict:
    """Generate backend code specifications using AI and templates"""

    # Extract entities from the prompts
    entities = spec_validator.extract_entities_from_prompts(
        backend_prompt.dict(),
        frontend_prompt.dict()
    )

    # Prepare prompt for backend AI agent
    ai_prompt = f"""
Based on the following backend engineering requirements, generate detailed specifications:

Role: {backend_prompt.role}
Domain: {backend_prompt.domain_description}
Project Context: {backend_prompt.project_context}
Technologies: {backend_prompt.required_technologies}
Deliverables: {backend_prompt.core_deliverables}
Constraints: {backend_prompt.constraints}

Current entities: {entities}

Generate additional entities or enhance existing ones based on the project requirements.
Return JSON with enhanced entity specifications including proper field types.

Format:
{{
  "entities": [
    {{
      "name": "EntityName",
      "fields": {{
        "field_name": "field_type"
      }}
    }}
  ]
}}
"""

    try:
        # Get AI-enhanced specifications
        ai_response = backend_client.generate(ai_prompt)
        import json
        ai_data = json.loads(ai_response)

        # Merge AI suggestions with extracted entities
        enhanced_entities = ai_data.get('entities', entities)

        return {
            "entities": enhanced_entities,
            "backend_prompt": backend_prompt.dict()
        }

    except Exception as e:
        # Fallback to extracted entities if AI fails
        return {
            "entities": entities,
            "backend_prompt": backend_prompt.dict()
        }