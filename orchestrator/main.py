"""FastAPI orchestrator"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from orchestrator.models import BuildRequest
from agents.manager import generate_manager_output
from agents.backend import generate_backend
from agents.frontend import generate_frontend
from providers.brainstorming_utils import gemini_list_items, gemini_generate_text

app = FastAPI(title="Kitchen Orchestrator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Kitchen API is running", "status": "healthy"}

@app.get("/output/backend/main.py")
async def get_backend_code():
    """Get generated backend code"""
    file_path = "output/backend/main.py"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "Backend code not found"}

@app.get("/output/frontend/index.html")
async def get_frontend_code():
    """Get generated frontend code"""
    file_path = "output/frontend/index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "Frontend code not found"}

@app.post("/build")
async def build(request: BuildRequest):
    """Build project from user prompt using correct system prompt"""
    # Generate manager output with backend and frontend prompts
    manager_output = await generate_manager_output(request.user_prompt)

    # Check if this is a frontend-only project
    if hasattr(manager_output, 'project_type') and manager_output.project_type == 'frontend_only':
        # Only generate frontend code
        await generate_frontend(manager_output.frontend_engineer_prompt)
        return {
            "status": "complete",
            "project_type": "frontend_only",
            "frontend_prompt": manager_output.frontend_engineer_prompt.dict()
        }
    else:
        # Generate both backend and frontend code
        await generate_backend(manager_output.backend_engineer_prompt)
        await generate_frontend(manager_output.frontend_engineer_prompt)
        return {
            "status": "complete",
            "project_type": "full_stack",
            "backend_prompt": manager_output.backend_engineer_prompt.dict(),
            "frontend_prompt": manager_output.frontend_engineer_prompt.dict()
        }

@app.post("/api/generate-ideas")
async def generate_ideas(request: dict):
    """Generate ideas based on niche, subNiche, and area using Gemini AI"""
    try:
        niche = request.get('niche', '')
        subNiche = request.get('subNiche', '')
        area = request.get('area', '')
        industry = request.get('industry', '')
        category = request.get('category', '')
        
        # Generate ideas using the brainstorming module
        if area and subNiche and niche:
            # Create a focused prompt for the specific area
            prompt = f"Generate 4 creative website ideas for {area} in {category} within {industry} industry. Each idea should be a complete business concept with unique value proposition."
            
            # Get AI-generated ideas
            ai_ideas = gemini_list_items(prompt, n=4)
            
            # Format the ideas into the expected structure
            formatted_ideas = []
            for i, idea in enumerate(ai_ideas, 1):
                formatted_ideas.append({
                    "id": i,
                    "title": idea,
                    "description": f"An innovative {area.lower()} solution that leverages modern technology to solve real-world problems in {industry.lower()}.",
                    "features": [
                        'Modern, intuitive user interface',
                        'Scalable cloud infrastructure', 
                        'Advanced analytics and reporting',
                        'Mobile-responsive design',
                        'Real-time data processing',
                        'Secure authentication system'
                    ]
                })
            
            return {"ideas": formatted_ideas}
        
        else:
            # Fallback to generic ideas if specific data is missing
            prompt = "Generate 4 creative website ideas for business automation and digital transformation. Each idea should be innovative and market-ready."
            ai_ideas = gemini_list_items(prompt, n=4)
            
            formatted_ideas = []
            for i, idea in enumerate(ai_ideas, 1):
                formatted_ideas.append({
                    "id": i,
                    "title": idea,
                    "description": f"A comprehensive business solution that streamlines operations and improves efficiency.",
                    "features": [
                        'Modern, intuitive user interface',
                        'Scalable cloud infrastructure',
                        'Advanced analytics and reporting',
                        'Mobile-responsive design'
                    ]
                })
            
            return {"ideas": formatted_ideas}
            
    except Exception as e:
        print(f"Error generating ideas: {e}")
        # Return fallback ideas if AI generation fails
        return {
            "ideas": [
                {
                    "id": 1,
                    "title": f"AI-Powered {request.get('area', 'Business Solution')}",
                    "description": f"An intelligent platform for {request.get('area', 'business automation')}",
                    "features": [
                        'Modern, intuitive user interface',
                        'Scalable cloud infrastructure',
                        'Advanced analytics and reporting',
                        'Mobile-responsive design'
                    ]
                }
            ]
        }

@app.post("/api/process-custom-idea")
async def process_custom_idea(request: dict):
    """Process a custom idea and generate project details using AI, then pass to manager agent"""
    try:
        idea_text = request.get('idea', '')
        audio_blob = request.get('audioBlob')  # Handle audio input if needed
        
        if not idea_text and not audio_blob:
            return {"error": "No idea provided"}
        
        # Use AI to analyze and expand the idea
        if idea_text:
            # Get AI analysis
            analysis_prompt = f"Analyze this business idea and provide a detailed project specification: '{idea_text}'. Include the target industry, key features, technology requirements, and potential challenges."
            ai_analysis = gemini_generate_text(analysis_prompt)
            
            # Generate project title
            title_prompt = f"Based on the idea '{idea_text}', generate a compelling project title (max 8 words):"
            project_title = gemini_generate_text(title_prompt)
            
            # Generate description
            desc_prompt = f"Write a brief description (2-3 sentences) for a project based on this idea: '{idea_text}'"
            project_description = gemini_generate_text(desc_prompt)
            
            # Create a comprehensive user prompt for the manager agent
            manager_prompt = f"""
            Create a web application based on this custom idea:
            
            Original Idea: {idea_text}
            Project Title: {project_title}
            Description: {project_description}
            Analysis: {ai_analysis}
            
            Please create a complete web application with both backend and frontend components. The backend should handle data management, API endpoints, and business logic. The frontend should provide an intuitive user interface for interacting with the application.
            
            Key Requirements:
            - Build a fully functional web application
            - Include proper database models and API endpoints
            - Create a modern, responsive user interface
            - Implement user authentication and data management
            - Ensure the application is ready for deployment
            """
            
            # Generate manager output with backend and frontend prompts
            manager_output = await generate_manager_output(manager_prompt)
            
            # Generate code using the specific prompts
            await generate_backend(manager_output.backend_engineer_prompt)
            await generate_frontend(manager_output.frontend_engineer_prompt)
            
            return {
                "idea": idea_text,
                "analysis": ai_analysis,
                "project_title": project_title,
                "description": project_description,
                "features": [
                    'Modern, intuitive user interface',
                    'Scalable architecture',
                    'Real-time data processing',
                    'Mobile-responsive design',
                    'Advanced analytics',
                    'Secure user authentication'
                ],
                "industry": "Technology",
                "category": "Custom Solution",
                "status": "complete",
                "backend_prompt": manager_output.backend_engineer_prompt.dict(),
                "frontend_prompt": manager_output.frontend_engineer_prompt.dict()
            }
        
    except Exception as e:
        print(f"Error processing custom idea: {e}")
        return {
            "error": "Failed to process idea",
            "fallback": {
                "idea": request.get('idea', 'Custom Project'),
                "project_title": f"AI-Powered {request.get('idea', 'Solution')}",
                "description": f"An innovative platform based on your idea: {request.get('idea', 'Custom Project')}",
                "features": [
                    'Modern, intuitive user interface',
                    'Scalable cloud infrastructure',
                    'Advanced analytics and reporting',
                    'Mobile-responsive design'
                ]
            }
        }

@app.post("/api/debug-code")
async def debug_code(request: dict):
    """Debug and fix code issues"""
    code = request.get("code", "")
    # Mock debugging logic
    return {
        "issues": [
            {
                "id": 1,
                "type": "warning",
                "severity": "medium",
                "title": "Missing Input Validation",
                "description": "User input is not being validated before processing.",
                "solution": "Add input validation middleware to sanitize and validate user data."
            }
        ],
        "fixed_code": code + "\n// Fixed: Added input validation"
    }