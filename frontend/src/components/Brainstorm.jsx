import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';

// Mock data for niche questions
const NICHE_DATA = {
  healthcare: {
    name: 'Healthcare',
    subNiches: {
      insurance: {
        name: 'Insurance',
        areas: [
          'Claims Processing',
          'Prior Authorization',
          'Provider Network Management',
          'Risk Assessment',
          'Policy Management'
        ]
      },
      clinical: {
        name: 'Clinical',
        areas: [
          'Patient Records',
          'Diagnosis Support',
          'Treatment Planning',
          'Medication Management',
          'Clinical Trials'
        ]
      },
      telemedicine: {
        name: 'Telemedicine',
        areas: [
          'Virtual Consultations',
          'Remote Monitoring',
          'Digital Prescriptions',
          'Patient Communication',
          'Health Data Analytics'
        ]
      }
    }
  },
  fintech: {
    name: 'Fintech',
    subNiches: {
      payments: {
        name: 'Payments',
        areas: [
          'Mobile Payments',
          'Cryptocurrency',
          'Cross-border Transfers',
          'Payment Processing',
          'Digital Wallets'
        ]
      },
      lending: {
        name: 'Lending',
        areas: [
          'Personal Loans',
          'Business Loans',
          'Credit Scoring',
          'Loan Management',
          'Risk Assessment'
        ]
      },
      investment: {
        name: 'Investment',
        areas: [
          'Robo-advisors',
          'Trading Platforms',
          'Portfolio Management',
          'Market Analysis',
          'Wealth Management'
        ]
      }
    }
  },
  ecommerce: {
    name: 'E-commerce',
    subNiches: {
      marketplace: {
        name: 'Marketplace',
        areas: [
          'Product Catalog',
          'Seller Management',
          'Order Processing',
          'Inventory Management',
          'Customer Reviews'
        ]
      },
      logistics: {
        name: 'Logistics',
        areas: [
          'Shipping Management',
          'Warehouse Operations',
          'Delivery Tracking',
          'Supply Chain',
          'Last-mile Delivery'
        ]
      },
      personalization: {
        name: 'Personalization',
        areas: [
          'Recommendation Engine',
          'Customer Segmentation',
          'Dynamic Pricing',
          'Behavioral Analytics',
          'A/B Testing'
        ]
      }
    }
  },
  education: {
    name: 'Education',
    subNiches: {
      online_learning: {
        name: 'Online Learning',
        areas: [
          'Course Management',
          'Student Assessment',
          'Learning Analytics',
          'Content Delivery',
          'Progress Tracking'
        ]
      },
      classroom: {
        name: 'Classroom Management',
        areas: [
          'Attendance Tracking',
          'Grade Management',
          'Parent Communication',
          'Resource Planning',
          'Student Behavior'
        ]
      },
      skills: {
        name: 'Skills Development',
        areas: [
          'Certification Programs',
          'Skill Assessment',
          'Career Guidance',
          'Mentorship Platform',
          'Industry Partnerships'
        ]
      }
    }
  }
};

function Brainstorm({ onComplete, projectData }) {
  const [hasIdea, setHasIdea] = useState(null);
  const [idea, setIdea] = useState(projectData.idea || '');
  const [selectedNiche, setSelectedNiche] = useState(projectData.niche || '');
  const [selectedSubNiche, setSelectedSubNiche] = useState(projectData.subNiche || '');
  const [selectedArea, setSelectedArea] = useState(projectData.specificArea || '');
  const [showIdeas, setShowIdeas] = useState(false);
  const [generatedIdeas, setGeneratedIdeas] = useState([]);
  const [selectedIdea, setSelectedIdea] = useState(null);
  const [isLoadingIdeas, setIsLoadingIdeas] = useState(false);
  
  // Audio recording state
  const [isAudioMode, setIsAudioMode] = useState(false);
  const [recordingState, setRecordingState] = useState({
    isRecording: false,
    audioBlob: null,
    audioUrl: null
  });
  const [animationLevel, setAnimationLevel] = useState(0);
  
  // Voice interaction state
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceResponse, setVoiceResponse] = useState('');
  const [isListening, setIsListening] = useState(false);
  
  // Voice flow state
  const [voiceFlowActive, setVoiceFlowActive] = useState(false);
  const [currentVoiceStep, setCurrentVoiceStep] = useState('');
  const [voiceFlowData, setVoiceFlowData] = useState({
    categories: [],
    subtopics: [],
    ideas: [],
    selectedCategory: '',
    selectedSubtopic: '',
    selectedIdea: ''
  });
  
  // Audio refs
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const sourceRef = useRef(null);

  // Generate a dynamic blob shape with smooth curves
  const generateBlobPath = (level) => {
    const r = 60 + level * 0.4; // Base radius with deformation
    const points = 10; // Number of control points
    const angleStep = (Math.PI * 2) / points;
    let pathData = [];

    for (let i = 0; i < points; i++) {
      const angle = i * angleStep;
      const radius = r + Math.sin(i * 2 + level * 0.05) * 2; // Creates a wavy effect
      const x = Math.cos(angle) * radius + 64; // Centering at 64,64
      const y = Math.sin(angle) * radius + 64;
      pathData.push([x, y]);
    }

    // Use d3.line to interpolate with cardinal curve (smooths out corners)
    const lineGenerator = d3
      .line()
      .curve(d3.curveCatmullRomClosed) // Smooth curved shape
      .x((d) => d[0])
      .y((d) => d[1]);

    const path = lineGenerator(pathData); // Returns the smooth SVG path
    return path || ''; // Return empty string if path is null
  };

  // Audio analysis for blob animation
  useEffect(() => {
    if (isListening) {
      navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        dataArrayRef.current = new Uint8Array(analyserRef.current.frequencyBinCount);

        sourceRef.current = audioContextRef.current.createMediaStreamSource(stream);
        sourceRef.current.connect(analyserRef.current);

        const detectSound = () => {
          if (analyserRef.current && dataArrayRef.current) {
            analyserRef.current.getByteFrequencyData(dataArrayRef.current);
            const volume = dataArrayRef.current.reduce((a, b) => a + b, 0) / dataArrayRef.current.length;
            setAnimationLevel(volume * 1.5);
            if (isListening) requestAnimationFrame(detectSound);
          }
        };
        detectSound();
      });
    } else {
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
      if (sourceRef.current) {
        sourceRef.current = null;
      }
    }
  }, [isListening]);

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
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecordingState(prev => ({ ...prev, isRecording: true }));
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

  const playRecording = () => {
    if (recordingState.audioUrl) {
      const audio = new Audio(recordingState.audioUrl);
      audio.play();
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
    setAnimationLevel(0);
  };

  // Voice interaction functions
  const speakText = async (text) => {
    if (!isVoiceEnabled) return;
    
    try {
      setIsSpeaking(true);
      const response = await fetch('http://localhost:5121/api/speak', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.audio) {
          // Convert base64 audio to blob and play
          const audioBlob = new Blob([Uint8Array.from(atob(data.audio), c => c.charCodeAt(0))], { type: 'audio/wav' });
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          
          audio.onended = () => {
            setIsSpeaking(false);
            URL.revokeObjectURL(audioUrl);
          };
          
          audio.play();
        }
      }
    } catch (error) {
      console.error('Error with text-to-speech:', error);
      setIsSpeaking(false);
    }
  };

  const askYesNoQuestion = async (question) => {
    if (!isVoiceEnabled) return null;
    
    while (true) {
      try {
        setIsListening(true);
        await speakText(question + " Please say yes or no.");
        
        // Wait for speech to finish before listening
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const response = await fetch('http://localhost:5121/api/ask-yes-no', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question })
        });
        
        if (response.ok) {
          const data = await response.json();
          setVoiceResponse(data.response);
          setIsListening(false);
          
          if (data.is_yes === true) {
            return true;
          } else if (data.is_yes === false) {
            return false;
          } else {
            // Invalid response, continue loop
            console.log("No valid response. Asking user to repeat.");
            continue;
          }
        }
      } catch (error) {
        console.error('Error with yes/no question:', error);
        setIsListening(false);
        return null;
      }
    }
  };

  const askDescription = async (question, maxSeconds = 20) => {
    if (!isVoiceEnabled) return '';
    
    try {
      setIsListening(true);
      await speakText(question);
      
      // Wait for speech to finish before listening
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const response = await fetch('http://localhost:5121/api/ask-description', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, max_seconds: maxSeconds })
      });
      
      if (response.ok) {
        const data = await response.json();
        setVoiceResponse(data.response);
        setIsListening(false);
        return data.response;
      }
    } catch (error) {
      console.error('Error with description question:', error);
      setIsListening(false);
    }
    return '';
  };

  const askChoiceFromList = async (question, options, allowNone = false, regenerateFunc = null) => {
    if (!isVoiceEnabled) return null;
    
    let currentOptions = [...options];
    let firstTime = true;
    
    while (true) {
      try {
        // Add "None of the above" if enabled
        const displayOptions = allowNone ? [...currentOptions, "None of the above"] : currentOptions;
        
        if (firstTime) {
          await speakText(question);
          console.log(`[System]: ${question}`);
          
          // Speak each option
          for (let i = 0; i < displayOptions.length; i++) {
            const optionText = `Option ${i + 1}: ${displayOptions[i]}`;
            await speakText(optionText);
            console.log(optionText);
          }
          
          await speakText(`Please say option 1 through option ${displayOptions.length}.`);
          console.log(`[System]: Please say option 1 through option ${displayOptions.length}.`);
          firstTime = false;
        } else {
          console.log("[System]: Asking user to repeat.");
          await speakText("Could you repeat again? Please say one of the options.");
        }
        
        setIsListening(true);
        
        // Wait for speech to finish before listening
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Get actual voice input using the backend
        const voiceResponse = await new Promise(async (resolve) => {
          try {
            const response = await fetch('http://localhost:5121/api/ask-description', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ question: '', max_seconds: 5 })
            });
            
            if (response.ok) {
              const data = await response.json();
              resolve(data.response || '');
            } else {
              resolve('');
            }
          } catch (error) {
            console.error('Error getting voice input:', error);
            resolve('');
          }
        });
        
        setVoiceResponse(voiceResponse);
        setIsListening(false);
        
        // Parse the response
        const response = voiceResponse.toLowerCase();
        
        // Check for option numbers
        for (let i = 0; i < displayOptions.length; i++) {
          if (response.includes(`option ${i + 1}`) || response.trim() === `${i + 1}` || response.includes(`number ${i + 1}`)) {
            const chosenOption = displayOptions[i];
            
            if (allowNone && chosenOption.toLowerCase().startsWith("none")) {
              if (regenerateFunc) {
                // Regenerate new options
                const newOptions = await regenerateFunc();
                currentOptions = newOptions;
                firstTime = true;
                break;
              }
            }
            
            return chosenOption;
          }
        }
        
        // If no valid option found, continue the loop
        console.log("Invalid response, asking again...");
        
      } catch (error) {
        console.error('Error with choice question:', error);
        setIsListening(false);
        return null;
      }
    }
  };

  // Dynamic content functions
  const getDynamicCategories = async () => {
    try {
      const response = await fetch('http://localhost:5121/api/get-categories');
      if (response.ok) {
        const data = await response.json();
        return data.categories;
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
    return ['Healthcare', 'Art', 'Education', 'E-commerce']; // Fallback
  };

  const getDynamicSubtopics = async (category) => {
    try {
      const response = await fetch('http://localhost:5121/api/get-subtopics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category })
      });
      if (response.ok) {
        const data = await response.json();
        return data.subtopics;
      }
    } catch (error) {
      console.error('Error fetching subtopics:', error);
    }
    return []; // Fallback
  };

  const getDynamicIdeas = async (category, subtopic) => {
    try {
      const response = await fetch('http://localhost:5121/api/get-ideas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category, subtopic })
      });
      if (response.ok) {
        const data = await response.json();
        return data.ideas;
      }
    } catch (error) {
      console.error('Error fetching ideas:', error);
    }
    return []; // Fallback
  };

  const processUserIdea = async (idea) => {
    try {
      const response = await fetch('http://localhost:5121/api/process-idea', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idea })
      });
      if (response.ok) {
        const data = await response.json();
        return data.result;
      }
    } catch (error) {
      console.error('Error processing idea:', error);
    }
    return null;
  };

  // Static ideas (fallback when backend is not available)
  const getStaticIdeas = () => {
    return [
      {
        id: 1,
        title: "AI-Powered Business Management Platform",
        description: "A comprehensive solution that automates business processes, provides intelligent insights, and streamlines operations across multiple departments.",
        features: [
          'Modern, intuitive user interface',
          'Scalable cloud infrastructure',
          'Advanced analytics and reporting',
          'Mobile-responsive design',
          'Integration capabilities'
        ]
      },
      {
        id: 2,
        title: "Smart Data Analytics Dashboard",
        description: "An intelligent dashboard that processes large datasets, provides real-time insights, and helps make data-driven business decisions.",
        features: [
          'Real-time data visualization',
          'Machine learning insights',
          'Customizable reports',
          'API integrations',
          'Automated alerts'
        ]
      },
      {
        id: 3,
        title: "Automated Workflow Management System",
        description: "A platform that automates complex business workflows, reduces manual tasks, and improves operational efficiency.",
        features: [
          'Workflow automation',
          'Task management',
          'Team collaboration tools',
          'Progress tracking',
          'Notification system'
        ]
      },
      {
        id: 4,
        title: "Customer Engagement Platform",
        description: "A comprehensive platform for managing customer relationships, improving engagement, and driving business growth.",
        features: [
          'Customer relationship management',
          'Communication tools',
          'Feedback collection',
          'Analytics and insights',
          'Multi-channel support'
        ]
      }
    ];
  };

  // Backend-ready idea generation (with fallback)
  const generateIdeas = async (niche, subNiche, area) => {
    try {
      const response = await fetch('http://localhost:5121/api/generate-ideas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          niche,
          subNiche,
          area,
          industry: NICHE_DATA[niche]?.name,
          category: NICHE_DATA[niche]?.subNiches[subNiche]?.name
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('🤖 AI Generated Ideas:', data.ideas);
        return data.ideas || getStaticIdeas();
      } else {
        console.warn('Backend API not available, using static ideas');
        return getStaticIdeas();
      }
    } catch (error) {
      console.warn('Error fetching ideas from backend:', error);
      return getStaticIdeas();
    }
  };

  const handleIdeaSubmit = async () => {
    if (idea.trim() || recordingState.audioBlob) {
      try {
        // Process the idea with AI first
        const response = await fetch('http://localhost:5121/api/process-custom-idea', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            idea: idea.trim() || 'Audio Recording',
            audioBlob: recordingState.audioBlob
          })
        });

        if (response.ok) {
          const data = await response.json();
          console.log('🤖 AI Processed Idea:', data);
          
          const formData = {
            idea: data.project_title || idea.trim() || 'Audio Recording',
            niche: data.industry || 'Custom Idea',
            subNiche: data.category || 'Custom Solution',
            specificArea: data.analysis || idea.trim(),
            audioBlob: recordingState.audioBlob,
            audioUrl: recordingState.audioUrl,
            aiAnalysis: data.analysis,
            features: data.features
          };
          
          console.log('🚀 AI-Enhanced Idea Submission:', formData);
          onComplete(formData);
        } else {
          // Fallback if AI processing fails
          const formData = {
            idea: idea.trim() || 'Audio Recording',
            niche: 'Custom Idea',
            subNiche: '',
            specificArea: '',
            audioBlob: recordingState.audioBlob,
            audioUrl: recordingState.audioUrl
          };
          
          console.log('🚀 Fallback Idea Submission:', formData);
          onComplete(formData);
        }
      } catch (error) {
        console.warn('Error processing idea with AI:', error);
        // Fallback submission
        const formData = {
          idea: idea.trim() || 'Audio Recording',
          niche: 'Custom Idea',
          subNiche: '',
          specificArea: '',
          audioBlob: recordingState.audioBlob,
          audioUrl: recordingState.audioUrl
        };
        
        console.log('🚀 Fallback Idea Submission:', formData);
        onComplete(formData);
      }
    }
  };

  const handleNicheSelection = async () => {
    if (selectedNiche && selectedSubNiche && selectedArea) {
      setIsLoadingIdeas(true);
      setShowIdeas(true);
      
      try {
        // Generate ideas (backend-ready with fallback)
        const ideas = await generateIdeas(selectedNiche, selectedSubNiche, selectedArea);
        setGeneratedIdeas(ideas);
        
        console.log('🎯 Generated Ideas:', ideas);
        console.log('📊 Selected Path:', {
          industry: NICHE_DATA[selectedNiche].name,
          category: NICHE_DATA[selectedNiche].subNiches[selectedSubNiche].name,
          focus: selectedArea
        });
      } catch (error) {
        console.error('Error generating ideas:', error);
        setGeneratedIdeas(getStaticIdeas());
      } finally {
        setIsLoadingIdeas(false);
      }
    }
  };

  const handleIdeaSelection = (idea) => {
    setSelectedIdea(idea);
    const formData = {
      idea: idea.title,
      niche: selectedNiche,
      subNiche: selectedSubNiche,
      specificArea: selectedArea
    };
    
    console.log('✅ Selected Idea:', formData);
    onComplete(formData);
  };

  const renderIdeaSelection = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Choose Your Idea!</h2>
        <p className="text-lg text-[#cccccc] mb-8">
          Based on your selection, here are some ideas to get you started:
        </p>
      </div>

      {isLoadingIdeas ? (
        <div className="max-w-6xl mx-auto text-center">
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
            <p className="text-white">Generating ideas...</p>
          </div>
        </div>
      ) : (
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {generatedIdeas.map((idea) => (
              <div
                key={idea.id}
                onClick={() => handleIdeaSelection(idea)}
                className={`p-6 rounded-[15px] border-2 cursor-pointer transition-all transform hover:scale-105 ${
                  selectedIdea?.id === idea.id
                    ? 'bg-white text-black border-white'
                    : 'bg-[#222222] border-[#444444] text-white hover:border-[#555555]'
                }`}
              >
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold">{idea.title}</h3>
                  <p className="text-sm opacity-80">{idea.description}</p>
                  
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium opacity-90">Key Features:</h4>
                    <ul className="text-xs space-y-1">
                      {idea.features.map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <span className="w-1.5 h-1.5 bg-current rounded-full mr-2 opacity-60"></span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="pt-2">
                    <span className="text-xs font-medium opacity-70">
                      Click to select this idea
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="text-center">
        <button
          onClick={() => {
            setShowIdeas(false);
            setSelectedNiche('');
            setSelectedSubNiche('');
            setSelectedArea('');
            setIsLoadingIdeas(false);
          }}
          className="px-6 py-2 bg-transparent border border-white hover:bg-white text-white hover:text-[#121212] rounded-[10px] transition-all"
        >
          Back to Selection
        </button>
      </div>
    </div>
  );

  const renderIdeaInput = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-medium text-white mb-4">Do you have an idea?</h2>
        {isVoiceEnabled && (
          <div className="mb-4">
            {isSpeaking && (
              <div className="text-lg text-blue-400 mb-2">🎤 Speaking...</div>
            )}
            {isListening && (
              <div className="text-lg text-green-400 mb-2">👂 Listening...</div>
            )}
            {voiceResponse && (
              <div className="text-lg text-yellow-400 mb-2">You said: "{voiceResponse}"</div>
            )}
          </div>
        )}
      </div>
      
      <div className="max-w-2xl mx-auto">
        {/* Audio Mode Toggle */}
        <div className="flex justify-center space-x-4 mb-4">
          <button
            onClick={() => {
              setIsAudioMode(!isAudioMode);
              if (!isAudioMode) {
                startRecording();
              }
            }}
            className={`px-6 py-3 rounded-[10px] transition-all ${
              isAudioMode 
                ? 'bg-white text-[#121212]' 
                : 'bg-transparent border border-white text-white hover:bg-white hover:text-[#121212]'
            }`}
          >
            Audio Mode
          </button>
          {!isVoiceEnabled && (
            <button
              onClick={() => setIsVoiceEnabled(true)}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-[10px] transition-all"
            >
              🎤 Enable Voice
            </button>
          )}
        </div>

        {isAudioMode ? (
          /* Audio Recording Interface */
          <div className="space-y-6">
            {recordingState.isRecording ? (
              <div className="flex flex-col items-center justify-center py-8">
                <svg className='h-[120px] w-[120px] overflow-visible' viewBox="0 0 128 128">
                  <defs>
                    <linearGradient id="blobGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#FF6600" />
                      <stop offset="100%" stopColor="#FFCC00" />
                    </linearGradient>
                  </defs>
                  <path d={generateBlobPath(animationLevel)} fill="url(#blobGradient)" />
                </svg>

                <button
                  onClick={stopRecording}
                  className="mt-10 px-6 py-2 bg-transparent border border-white hover:bg-white text-white hover:text-[#121212] rounded-[10px] transition-all"
                >
                  Stop Recording
                </button>
              </div>
            ) : recordingState.audioUrl ? (
              /* Playback Interface */
              <div className="flex flex-col items-center justify-center py-8">

                <p className="text-white mb-14 text-center">
                  Recording complete!
                </p>
                <div className="flex space-x-4">
                  <button
                    onClick={playRecording}
                    className="px-6 py-2 bg-white hover:bg-[#f0f0f0] text-[#121212] rounded-[10px] transition-all"
                  >
                    Play
                  </button>
                  <button
                    onClick={resetRecording}
                    className="px-6 py-2 bg-transparent border border-white hover:bg-white text-white hover:text-[#121212] rounded-[10px] transition-all"
                  >
                    Record Again
                  </button>
                </div>
                <div className="mt-6">
                  <button
                    onClick={handleIdeaSubmit}
                    disabled={!recordingState.audioBlob}
                    className="px-8 py-3 bg-white hover:bg-[#f0f0f0] disabled:bg-transparent disabled:border disabled:border-white disabled:text-white text-[#121212] rounded-[10px] transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
                  >
                    Continue to Code
                  </button>
                </div>
              </div>
            ) : (
              /* Start Recording Interface - This should not show since recording starts automatically */
              <div className="flex flex-col items-center justify-center py-8">
                <div className="w-24 h-24 bg-transparent border border-white rounded-full flex items-center justify-center mb-4">
                  <div className="w-8 h-8 bg-white rounded-full"></div>
                </div>
                <p className="text-white mb-4 text-center">
                  Starting recording...
                </p>
              </div>
            )}
          </div>
        ) : (
          /* Text Input Interface */
          <>
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="Describe your idea... What problem are you solving? Who is your target audience? What makes your solution unique?"
              className="w-full h-32 px-4 py-3 bg-[#222222] border border-[#444444] rounded-[10px] text-white placeholder-[#666666] focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
            
            <div className="mt-4 flex justify-center">
              <button
                onClick={handleIdeaSubmit}
                disabled={!idea.trim()}
                className="px-8 py-3 bg-white hover:bg-[#f0f0f0] disabled:bg-transparent disabled:border disabled:border-white disabled:text-white text-[#121212] rounded-[10px] transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
              >
                Continue to Code
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );

  const renderNicheQuestions = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Let's find your niche!</h2>
        {isVoiceEnabled && (
          <div className="mb-4">
            {isSpeaking && (
              <div className="text-lg text-blue-400 mb-2">🎤 Speaking...</div>
            )}
            {isListening && (
              <div className="text-lg text-green-400 mb-2">👂 Listening...</div>
            )}
            {voiceResponse && (
              <div className="text-lg text-yellow-400 mb-2">You said: "{voiceResponse}"</div>
            )}
          </div>
        )}
      </div>

      {/* Step 1: Select Main Niche */}
      <div className="max-w-4xl mx-auto">
        <h3 className="text-xl  text-white mb-4">1. What industry interests you most?</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(NICHE_DATA).map(([key, niche]) => (
            <button
              key={key}
              onClick={() => {
                setSelectedNiche(key);
                setSelectedSubNiche('');
                setSelectedArea('');
              }}
              className={`p-4 rounded-[10px] border transition-all ${
                selectedNiche === key
                  ? 'bg-white text-[#121212] border-white'
                  : 'bg-transparent border-white text-white hover:bg-white hover:text-[#121212]'
              }`}
            >
              <div className="text-center">
                <div className="">{niche.name}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Step 2: Select Sub-niche */}
      {selectedNiche && (
        <div className="max-w-4xl mx-auto">
          <h3 className="text-xl  text-white mb-4">2. What specific area within {NICHE_DATA[selectedNiche].name}?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(NICHE_DATA[selectedNiche].subNiches).map(([key, subNiche]) => (
              <button
                key={key}
                onClick={() => {
                  setSelectedSubNiche(key);
                  setSelectedArea('');
                }}
                className={`p-4 rounded-[10px] border transition-all ${
                  selectedSubNiche === key
                    ? 'bg-white text-[#121212] border-white'
                    : 'bg-transparent border-white text-white hover:bg-white hover:text-[#121212]'
                }`}
              >
                <div className="">{subNiche.name}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Select Specific Area */}
      {selectedSubNiche && (
        <div className="max-w-4xl mx-auto">
          <h3 className="text-xl  text-white mb-4">3. What specific problem do you want to solve?</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {NICHE_DATA[selectedNiche].subNiches[selectedSubNiche].areas.map((area) => (
              <button
                key={area}
                onClick={() => setSelectedArea(area)}
                className={`p-3 rounded-[10px] border transition-all ${
                  selectedArea === area
                    ? 'bg-white text-[#121212] border-white'
                    : 'bg-transparent border-white text-white hover:bg-white hover:text-[#121212]'
                }`}
              >
                <div className="text-sm font-medium">{area}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Continue Button */}
      {selectedArea && (
        <div className="flex justify-center">
          <button
            onClick={handleNicheSelection}
            className="px-8 py-3 bg-white hover:bg-[#f0f0f0] text-[#121212] rounded-[10px] transition-all transform hover:scale-105"
          >
            Continue to Code
          </button>
        </div>
      )}
    </div>
  );

  // Complete voice flow implementation
  const startCompleteVoiceFlow = async () => {
    setIsVoiceEnabled(true);
    setVoiceFlowActive(true);
    setCurrentVoiceStep('initial_question');
    
    try {
      // Call the complete voice flow endpoint
      const response = await fetch('http://localhost:5121/api/complete-voice-flow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.flow_complete) {
          console.log('✅ Voice flow completed successfully!');
          console.log('Check the backend console for the complete conversation and results.');
          
          // Since the backend handles the complete flow, we'll just show a success message
          // The user can check the backend console for the results
          alert('Voice flow completed! Check the backend console for results.');
          
          // For now, we'll complete with a generic success
          const formData = {
            idea: 'Voice flow completed - check backend console',
            niche: 'Voice Generated',
            subNiche: '',
            specificArea: ''
          };
          
          onComplete(formData);
        }
      } else {
        console.error('Error in voice flow:', response.statusText);
      }
    } catch (error) {
      console.error('Error in voice flow:', error);
    } finally {
      setVoiceFlowActive(false);
      setCurrentVoiceStep('');
    }
  };

  // Voice bubble component
  const renderVoiceBubble = () => {
    if (!voiceFlowActive) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-[#121212] rounded-[20px] p-8 max-w-2xl mx-4">
          <div className="text-center space-y-6">
            <h2 className="text-2xl font-bold text-white mb-6">Voice Chat Active</h2>
            
            {/* Voice Bubble */}
            <div className="flex justify-center mb-6">
              <svg className='h-[200px] w-[200px] overflow-visible' viewBox="0 0 128 128">
                <defs>
                  <linearGradient id="voiceGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#FF6600" />
                    <stop offset="100%" stopColor="#FFCC00" />
                  </linearGradient>
                </defs>
                <path 
                  d={generateBlobPath(isListening ? animationLevel : 0)} 
                  fill="url(#voiceGradient)" 
                />
              </svg>
            </div>
            
            {/* Status Messages */}
            <div className="space-y-3">
              {isSpeaking && (
                <div className="text-lg text-blue-400">🎤 System is speaking...</div>
              )}
              {isListening && (
                <div className="text-lg text-green-400">👂 Listening for your response...</div>
              )}
              {!isSpeaking && !isListening && (
                <div className="text-lg text-yellow-400">⏳ Processing...</div>
              )}
            </div>
            
            {/* Current Step */}
            {currentVoiceStep && (
              <div className="text-sm text-gray-400">
                {currentVoiceStep === 'initial_question' && 'Starting voice conversation...'}
                {currentVoiceStep === 'listening_yes_no' && 'Waiting for yes/no response...'}
                {currentVoiceStep === 'description' && 'Getting your idea description...'}
                {currentVoiceStep === 'listening_description' && 'Listening to your description...'}
                {currentVoiceStep === 'listening_choice' && 'Waiting for your choice...'}
              </div>
            )}
            
            {/* Voice Flow Status */}
            <div className="text-sm text-gray-400">
              Complete voice flow is running in the background.
              <br />
              Follow the voice prompts to complete the conversation.
            </div>
            
            {/* Voice Response Display */}
            {voiceResponse && (
              <div className="bg-[#222222] rounded-[10px] p-4">
                <div className="text-sm text-gray-400 mb-2">You said:</div>
                <div className="text-white">"{voiceResponse}"</div>
              </div>
            )}
            
            {/* Stop Button */}
            <button
              onClick={() => {
                setVoiceFlowActive(false);
                setIsVoiceEnabled(false);
                setCurrentVoiceStep('');
              }}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-[10px] transition-all"
            >
              Stop Voice Chat
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto">
      {showIdeas ? (
        renderIdeaSelection()
      ) : hasIdea === null ? (
        <div className="text-center space-y-16 pt-20">
          <div>
            <h1 className="text-4xl font-medium text-white mb-4">Let's get started!</h1>
          </div>
          
          <div className="flex justify-center space-x-6">
            <button
              onClick={startCompleteVoiceFlow}
              disabled={voiceFlowActive}
              className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-[10px] transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
            >
              {voiceFlowActive ? 'Voice Chat Active...' : '🎤 Start Complete Voice Flow'}
            </button>
            <button
              onClick={() => setHasIdea(true)}
              className="px-8 py-4 bg-white hover:bg-[#f0f0f0] text-[#121212] rounded-[10px] transition-all transform hover:scale-105"
            >
              Yes, I have an idea!
            </button>
            <button
              onClick={() => setHasIdea(false)}
              className="px-8 py-4 bg-transparent border border-white hover:bg-white text-white hover:text-[#121212] rounded-[10px] transition-all transform hover:scale-105"
            >
              Help me find one
            </button>
          </div>
        </div>
      ) : hasIdea ? (
        renderIdeaInput()
      ) : (
        renderNicheQuestions()
      )}
      
      {/* Voice Bubble Overlay */}
      {renderVoiceBubble()}
    </div>
  );
}

export default Brainstorm;