import React, { useState } from 'react';
import Brainstorm from './components/Brainstorm';
import Code from './components/Code';
import Review from './components/Review';
import Deploy from './components/Deploy';
import CodePanel from './components/CodePanel';

const WORKFLOW_STEPS = {
  BRAINSTORM: 'brainstorm',
  CODE: 'code',
  REVIEW: 'review',
  DEPLOY: 'deploy'
};

function App() {
  const [currentStep, setCurrentStep] = useState(WORKFLOW_STEPS.BRAINSTORM);
  const [showCodePanel, setShowCodePanel] = useState(false);
  const [projectData, setProjectData] = useState({
    idea: '',
    niche: '',
    subNiche: '',
    specificArea: '',
    generatedCode: '',
    debugIssues: [],
    deploymentStatus: 'pending'
  });

  const handleStepComplete = (stepData) => {
    setProjectData(prev => ({ ...prev, ...stepData }));
    
    // Handle special cases for step navigation
    if (stepData.reviewStatus === 'needs_changes') {
      // Go back to debug step
      setCurrentStep(WORKFLOW_STEPS.DEBUG);
      return;
    }
    
    // Move to next step
    const stepOrder = Object.values(WORKFLOW_STEPS);
    const currentIndex = stepOrder.indexOf(currentStep);
    if (currentIndex < stepOrder.length - 1) {
      setCurrentStep(stepOrder[currentIndex + 1]);
    }
  };

  const resetWorkflow = () => {
    setCurrentStep(WORKFLOW_STEPS.BRAINSTORM);
    setProjectData({
      idea: '',
      niche: '',
      subNiche: '',
      specificArea: '',
      generatedCode: '',
      debugIssues: [],
      deploymentStatus: 'pending'
    });
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case WORKFLOW_STEPS.BRAINSTORM:
        return <Brainstorm onComplete={handleStepComplete} projectData={projectData} />;
      case WORKFLOW_STEPS.CODE:
        return <Code onComplete={handleStepComplete} projectData={projectData} />;
      case WORKFLOW_STEPS.REVIEW:
        return <Review onComplete={handleStepComplete} projectData={projectData} />;
      case WORKFLOW_STEPS.DEPLOY:
        return <Deploy onComplete={handleStepComplete} projectData={projectData} />;
      default:
        return <Brainstorm onComplete={handleStepComplete} projectData={projectData} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#121212]">
      {/* Header */}
      <header className="bg-[#222222] border-b border-[#374151]">
        <div className=" mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">

              <h1 className="text-2xl font-medium text-white">Kitchen</h1>
            </div>

          </div>
        </div>
      </header>

      <div className="flex">
        {/* Code Panel */}
        <CodePanel 
          isOpen={showCodePanel} 
          onClose={() => setShowCodePanel(false)} 
          generatedCode={projectData.generatedCode}
        />

        {/* Main Content */}
        <div className={`transition-all duration-500 ease-in-out ${
          showCodePanel ? 'w-3/5' : 'w-full'
        }`}>
      {/* Steps Bar */}
      <div className="">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-4">
          <div className="flex items-center justify-center">
            {Object.entries(WORKFLOW_STEPS).map(([key, value], index) => {
              const isActive = currentStep === value;
              const isCompleted = Object.values(WORKFLOW_STEPS).indexOf(currentStep) > index;
              
              return (
                <div key={value} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full text-[16px] font-medium transition duration-200 ${
                    isCompleted || isActive
                      ? 'bg-white text-black' 
                      : 'bg-[#343434] text-white'
                  }`}>
                    {index + 1}
                  </div>
                  {index < Object.keys(WORKFLOW_STEPS).length - 1 && (
                    <div className="relative w-8 h-1 bg-[#343434] overflow-hidden ">
                      <div 
                        className={`absolute top-0 left-0 h-full bg-white transition-all duration-500 ease-in-out ${
                          isCompleted ? 'w-full' : 'w-0'
                        }`}
                        style={{
                          transitionDelay: isCompleted ? '200ms' : '0ms'
                        }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

          {/* Main Content */}
          <main className="mx-auto px-4 sm:px-6 lg:px-8 py-4">
            {renderCurrentStep()}
          </main>
        </div>
      </div>

      {/* Floating Code Toggle Button */}
      {!showCodePanel && (
        <button
          onClick={() => setShowCodePanel(true)}
          className="fixed bottom-6 left-6 bg-white hover:bg-[#f0f0f0] text-[#121212] p-4 rounded-full shadow-lg transition-all transform hover:scale-105 z-50"
          title="Show Generated Code"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
        </button>
      )}
    </div>
  );
}

export default App;
