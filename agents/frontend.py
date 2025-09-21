"""Frontend agent: generates code from frontend prompt"""

from ..orchestrator.models import FrontendPrompt
from ..providers.gemini import frontend_client


async def generate_frontend_code(frontend_prompt: FrontendPrompt, entities: list) -> dict:
    """Generate frontend code specifications using AI"""

    # Prepare prompt for frontend AI agent
    ai_prompt = f"""
Based on the following frontend engineering requirements, generate UI/UX specifications:

Role: {frontend_prompt.role}
Domain: {frontend_prompt.domain_description}
Project Context: {frontend_prompt.project_context}
Technologies: {frontend_prompt.required_technologies}
Deliverables: {frontend_prompt.core_deliverables}
API Integration: {frontend_prompt.api_integration_requirements}
Constraints: {frontend_prompt.constraints}

Available entities: {entities}

Generate page specifications and UI components for the project.
Return JSON with page and component specifications.

Format:
{{
  "pages": [
    {{
      "name": "PageName",
      "route": "/route",
      "components": ["ComponentName"],
      "entities_used": ["EntityName"]
    }}
  ],
  "components": [
    {{
      "name": "ComponentName",
      "type": "list|form|detail",
      "entity": "EntityName"
    }}
  ]
}}
"""

    try:
        # Get AI-enhanced specifications
        ai_response = frontend_client.generate(ai_prompt)
        import json
        ai_data = json.loads(ai_response)

        return {
            "pages": ai_data.get('pages', []),
            "components": ai_data.get('components', []),
            "frontend_prompt": frontend_prompt.dict()
        }

    except Exception:
        # Fallback to default page structure
        return {
            "pages": [
                {
                    "name": "HomePage",
                    "route": "/",
                    "components": ["Navigation", "Dashboard"],
                    "entities_used": [entity["name"] for entity in entities]
                }
            ],
            "components": [
                {
                    "name": "Navigation",
                    "type": "navigation",
                    "entity": None
                },
                {
                    "name": "Dashboard",
                    "type": "dashboard",
                    "entity": None
                }
            ],
            "frontend_prompt": frontend_prompt.dict()
        }