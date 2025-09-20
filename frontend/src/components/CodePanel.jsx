import React from 'react';

function CodePanel({ isOpen, onClose, generatedCode }) {
  return (
    <div className={`transition-all duration-500 ease-in-out overflow-hidden ${
      isOpen ? 'w-2/5' : 'w-0'
    }`}>
      <div className="h-screen bg-[#1a1a1a] border-r border-[#343434] p-6">
        <div className="flex items-center justify-end mb-6">
          <button
            onClick={onClose}
            className="text-[#888888] hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {generatedCode ? (
          <div className="bg-[#121212] rounded-lg p-4 overflow-auto h-[calc(100vh-120px)]">
            <pre className="text-green-400 text-sm">
              <code>{generatedCode}</code>
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-[calc(100vh-120px)]">
            <div className="text-center">
              <div className="text-4xl mb-4 text-[#888888]">💻</div>
              <p className="text-[#888888]">No code generated yet</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CodePanel;
