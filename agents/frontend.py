"""Frontend agent: generates code from frontend prompt"""

import os
from ..orchestrator.models import FrontendPrompt


async def generate_frontend(frontend_prompt: FrontendPrompt) -> None:
    """Generate frontend code from frontend prompt"""
    os.makedirs("output/frontend", exist_ok=True)

    # Generate HTML
    html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frontend Application</title>
    <style>
        /* {frontend_prompt.role} */
        /* {frontend_prompt.domain_description} */
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .content {{
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Frontend Application</h1>
            <p>Project Context: {frontend_prompt.project_context}</p>
        </div>
        <div class="content">
            <h2>Core Deliverables:</h2>
            <ul>
                {"".join(f"<li>{deliverable}</li>" for deliverable in frontend_prompt.core_deliverables)}
            </ul>

            <h2>API Integration:</h2>
            <ul>
                {"".join(f"<li>{req}</li>" for req in frontend_prompt.api_integration_requirements)}
            </ul>
        </div>
    </div>

    <script>
        // {frontend_prompt.required_technologies.get('scripting', 'Vanilla JavaScript ES6+')}
        console.log('Frontend application loaded');

        // API integration example
        async function fetchData() {{
            try {{
                const response = await fetch('/api/data');
                const data = await response.json();
                console.log('Data fetched:', data);
            }} catch (error) {{
                console.error('Error fetching data:', error);
            }}
        }}

        // Initialize app
        document.addEventListener('DOMContentLoaded', () => {{
            console.log('App initialized');
        }});
    </script>
</body>
</html>'''

    # Write file
    with open("output/frontend/index.html", "w") as f:
        f.write(html_code)