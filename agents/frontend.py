"""Frontend agent: generates code from frontend prompt"""

import os
from orchestrator.models import FrontendPrompt


async def generate_frontend(frontend_prompt: FrontendPrompt) -> None:
    """Generate frontend code from frontend prompt using LLM"""
    os.makedirs("output/frontend", exist_ok=True)
    
    from providers.gemini import gemini_client
    
    # Create a comprehensive prompt for the LLM to generate the frontend code
    llm_prompt = f"""
    You are a Frontend Engineer. Generate a complete, functional HTML file based on the following requirements:

    Role: {frontend_prompt.role}
    Domain Description: {frontend_prompt.domain_description}
    Project Context: {frontend_prompt.project_context}
    
    Required Technologies:
    - Markup: {frontend_prompt.required_technologies.get('markup', 'HTML5')}
    - Styling: {frontend_prompt.required_technologies.get('styling', 'CSS3')}
    - Scripting: {frontend_prompt.required_technologies.get('scripting', 'Vanilla JavaScript ES6+')}
    
    Code Requirements: {', '.join(frontend_prompt.code_requirements)}
    Core Deliverables: {', '.join(frontend_prompt.core_deliverables)}
    API Integration Requirements: {', '.join(frontend_prompt.api_integration_requirements) if frontend_prompt.api_integration_requirements else 'None'}
    Constraints: {', '.join(frontend_prompt.constraints)}
    
    Generate a complete, functional HTML file that includes:
    1. All HTML structure
    2. All CSS styling (embedded in <style> tags)
    3. All JavaScript functionality (embedded in <script> tags)
    4. The file should be immediately executable and functional
    5. Make it visually appealing and user-friendly
    6. Ensure it works as a single file (no external dependencies)
    
    Return ONLY the complete HTML code, nothing else.
    """
    
    # Generate the HTML code using the LLM
    html_code = gemini_client.generate(llm_prompt)
    
    # Handle if the LLM returns JSON instead of raw HTML
    if html_code.strip().startswith('{'):
        try:
            import json
            data = json.loads(html_code)
            if 'html' in data:
                html_code = data['html']
        except:
            pass  # If JSON parsing fails, use the original response
    
    # Write file
    with open("output/frontend/index.html", "w") as f:
        f.write(html_code)