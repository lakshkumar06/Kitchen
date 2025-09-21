import React, { useState, useEffect } from 'react';

function Code({ onComplete, projectData }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('');
  const [generationStatus, setGenerationStatus] = useState('');

  useEffect(() => {
    // Start code generation when component mounts
    if (projectData.idea) {
      generateCode();
    }
  }, [projectData]);

  const generateCode = async () => {
    setIsGenerating(true);
    setGenerationStatus('Analyzing project requirements...');
    
    try {
      // Create a comprehensive prompt for the manager agent
      const userPrompt = `
      Create a complete web application based on this project idea:
      
      Project Idea: ${projectData.idea}
      Industry: ${projectData.niche || 'Technology'}
      Category: ${projectData.subNiche || 'Web Application'}
      Specific Area: ${projectData.specificArea || 'General Application'}
      
      ${projectData.aiAnalysis ? `AI Analysis: ${projectData.aiAnalysis}` : ''}
      
      Please create a fully functional web application with:
      - Backend API with proper database models and endpoints
      - Frontend interface with modern, responsive design
      - User authentication and data management
      - Ready for deployment
      `;

      setGenerationStatus('Generating backend architecture...');
      
      // Call the build endpoint to generate code
      const response = await fetch('http://localhost:8000/build', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_prompt: userPrompt
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('🚀 Code Generation Response:', data);
        
        setGenerationStatus('Generating frontend interface...');
        
        // Get the generated code files
        const backendCode = await fetch('http://localhost:8000/output/backend/main.py').then(r => r.text()).catch(() => '');
        const frontendCode = await fetch('http://localhost:8000/output/frontend/index.html').then(r => r.text()).catch(() => '');
        
        // Combine backend and frontend code for display
        const combinedCode = `
// BACKEND CODE (Python/FastAPI)
${backendCode}

// FRONTEND CODE (HTML/CSS/JS)
${frontendCode}
        `.trim();
        
        setGeneratedCode(combinedCode);
        setSelectedLanguage('Python + HTML/CSS/JS');
        setSelectedFramework('FastAPI + Vanilla JS');
        setGenerationStatus('Code generation complete!');
        
        // Automatically proceed to review after code generation
        handleContinue();
        
      } else {
        throw new Error('Failed to generate code');
      }
      
    } catch (error) {
      console.error('Error generating code:', error);
      setGenerationStatus('Error generating code. Using fallback...');
      
      // Fallback code generation
      const fallbackCode = `// Generated for: ${projectData.idea}
// Backend (Python/FastAPI)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="${projectData.idea}")

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
def read_root():
    return {"message": "${projectData.idea} API is running"}

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}

// Frontend (HTML/CSS/JS)
<!DOCTYPE html>
<html>
<head>
    <title>${projectData.idea}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>${projectData.idea}</h1>
        <p>Welcome to your application!</p>
    </div>
</body>
</html>`;
      
      setGeneratedCode(fallbackCode);
      setSelectedLanguage('Python + HTML');
      setSelectedFramework('FastAPI + Vanilla JS');
      
      handleContinue();
    }
    
    setIsGenerating(false);
  };

  const handleContinue = () => {
    onComplete({
      generatedCode,
      language: selectedLanguage,
      framework: selectedFramework,
      status: 'complete'
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {isGenerating ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="relative mb-8">
            <div className="w-24 h-24 border-4 border-[#343434] border-t-white rounded-full animate-spin"></div>
          </div>
          <h3 className="text-2xl font-semibold text-white mb-2">Generating Code...</h3>
          <p className="text-[#888888] text-center">{generationStatus}</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Generation Results */}
          <div className="rounded-lg pt-16 text-center">
            <div className="mb-16">
              <div className="text-6xl font-bold text-white mb-2">✓</div>
              <div className="text-[16px] text-[#888888]">Code Generated Successfully</div>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-2xl font-medium text-white mb-1">{selectedLanguage}</div>
                <div className="text-md text-[#888888]">Programming Language</div>
              </div>
              <div>
                <div className="text-2xl font-medium text-white mb-1">{selectedFramework}</div>
                <div className="text-md text-[#888888]">Framework</div>
              </div>
            </div>

            <div className="mt-16">
              <div className="inline-flex items-center space-x-2 px-6 py-3 bg-white text-[#121212] rounded-lg">
                <span className="font-semibold">Code generation complete!</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Code;