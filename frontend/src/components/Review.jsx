import React, { useState, useRef } from 'react';

// Get the actual generated HTML content
const getGeneratedHTML = async () => {
  try {
    const response = await fetch('http://localhost:8000/output/frontend/index.html');
    if (response.ok) {
      return await response.text();
    }
  } catch (error) {
    console.error('Error fetching generated HTML:', error);
  }
  
  // Fallback HTML if generation fails
  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generated Project</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Generated Project</h1>
            <p>Your project has been successfully generated! This is a preview of your application.</p>
        </div>
    </body>
    </html>
  `;
};

function Review({ onComplete, projectData }) {
  const [isLoading, setIsLoading] = useState(true);
  const [projectHTML, setProjectHTML] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingState, setRecordingState] = useState({
    isRecording: false,
    audioBlob: null,
    audioUrl: null
  });
  
  // Audio refs
  const mediaRecorderRef = useRef(null);

  React.useEffect(() => {
    // Load the actual generated HTML
    const loadProject = async () => {
      try {
        const html = await getGeneratedHTML();
        setProjectHTML(html);
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading project:', error);
        setIsLoading(false);
      }
    };

    loadProject();
  }, [projectData]);

  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setRecordingState({
          isRecording: false,
          audioBlob: audioBlob,
          audioUrl: audioUrl
        });
        setIsRecording(false);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecordingState(prev => ({ ...prev, isRecording: true }));
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingState.isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const handleContinue = () => {
    onComplete({
      reviewedHTML: projectHTML,
      reviewStatus: 'approved'
    });
  };

  const handleNeedChanges = () => {
    if (recordingState.audioBlob) {
      // If we have a recording, proceed with it
      onComplete({
        reviewStatus: 'needs_changes',
        audioBlob: recordingState.audioBlob,
        audioUrl: recordingState.audioUrl
      });
    } else {
      // Start recording
      startRecording();
    }
  };

  const resetRecording = () => {
    if (recordingState.audioUrl) {
      URL.revokeObjectURL(recordingState.audioUrl);
    }
    setRecordingState({
      isRecording: false,
      audioBlob: null,
      audioUrl: null
    });
    setIsRecording(false);
  };

  return (
    <div className="max-w-7xl mx-auto ">
      <div className="text-center flex justify-between pb-4">
        <h2 className="text-3xl font-medium text-white mb-4">Need Changes?</h2>
        <div className="flex gap-2">
          {isRecording ? (
            <button
              onClick={stopRecording}
              className="px-8 py-2 bg-white text-[#121212] rounded-[10px] transition-all transform flex items-center gap-2"
            >
              <div className="flex items-center gap-1">
                <div className="w-1 h-3 bg-[#121212] animate-pulse"></div>
                <div className="w-1 h-4 bg-[#121212] animate-pulse" style={{animationDelay: '0.1s'}}></div>
                <div className="w-1 h-3 bg-[#121212] animate-pulse" style={{animationDelay: '0.2s'}}></div>
                <div className="w-1 h-2 bg-[#121212] animate-pulse" style={{animationDelay: '0.3s'}}></div>
              </div>
              Stop
            </button>
          ) : recordingState.audioBlob ? (
            <div className="flex gap-2">
              <button
                onClick={handleNeedChanges}
                className="px-8 py-2 bg-white hover:bg-[#f0f0f0] text-[#121212] rounded-[10px] transition-all transform"
              >
                Submit Changes
              </button>
              <button
                onClick={resetRecording}
                className="px-6 py-2 bg-transparent border border-white hover:bg-white text-white hover:text-[#121212] rounded-[10px] transition-all transform"
              >
                Record Again
              </button>
            </div>
          ) : (
            <button
              onClick={handleNeedChanges}
              className="px-8 py-2 bg-transparent border border-white hover:bg-white text-white hover:text-[#121212] rounded-[10px] transition-all transform"
            >
              Need Changes
            </button>
          )}
          <button
            onClick={handleContinue}
            className="px-8 py-2 bg-white hover:bg-[#f0f0f0] text-[#121212] rounded-[10px] transition-all transform"
          >
            Looks Good
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-20 h-20 border-4 border-[#343434] border-t-white rounded-full animate-spin mb-6"></div>
          <h3 className="text-2xl font-semibold text-white mb-2">Loading Project Preview...</h3>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Project Preview */}
          <div className="bg-[#222222] rounded-[15px] p-6">
            <div className="flex items-center justify-end mb-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
            </div>
            
            <div className="bg-white rounded-[10px] overflow-hidden" style={{ height: '600px' }}>
              <iframe
                srcDoc={projectHTML}
                className="w-full h-full border-0"
                title="Project Preview"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
              />
            </div>
          </div>

         
        </div>
      )}
    </div>
  );
}

export default Review;
