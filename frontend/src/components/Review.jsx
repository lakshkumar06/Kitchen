import React, { useState, useRef } from 'react';

// Mock HTML content for the project preview
const generateProjectHTML = (projectData) => {
  const idea = projectData.idea || 'Sample Project';
  const niche = projectData.niche || 'Technology';
  
  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${idea}</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            
            .container {
                max-width: 800px;
                padding: 2rem;
                text-align: center;
            }
            
            .logo {
                width: 80px;
                height: 80px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                margin: 0 auto 2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                font-weight: bold;
            }
            
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                font-weight: 700;
            }
            
            .subtitle {
                font-size: 1.2rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin: 3rem 0;
            }
            
            .feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
            
            .feature h3 {
                margin-bottom: 0.5rem;
                font-size: 1.1rem;
            }
            
            .feature p {
                opacity: 0.8;
                font-size: 0.9rem;
            }
            
            .cta-button {
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 1rem 2rem;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 2rem;
            }
            
            .cta-button:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            
            @media (max-width: 768px) {
                h1 {
                    font-size: 2rem;
                }
                
                .container {
                    padding: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">${idea.charAt(0).toUpperCase()}</div>
            <h1>${idea}</h1>
            <p class="subtitle">A modern ${niche} solution built with cutting-edge technology</p>
            
            <div class="features">
                <div class="feature">
                    <h3>Modern Design</h3>
                    <p>Clean, intuitive interface that users love</p>
                </div>
                <div class="feature">
                    <h3>Fast Performance</h3>
                    <p>Optimized for speed and efficiency</p>
                </div>
                <div class="feature">
                    <h3>Scalable Architecture</h3>
                    <p>Built to grow with your business</p>
                </div>
            </div>
            
            <button class="cta-button">Get Started</button>
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
    // Simulate loading the project
    const timer = setTimeout(() => {
      const html = generateProjectHTML(projectData);
      setProjectHTML(html);
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
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
                sandbox="allow-scripts"
              />
            </div>
          </div>

         
        </div>
      )}
    </div>
  );
}

export default Review;
