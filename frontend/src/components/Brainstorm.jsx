import React, { useState } from 'react';

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
      // TODO: Replace with actual backend API endpoint
      const response = await fetch('/api/generate-ideas', {
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

  const handleIdeaSubmit = () => {
    if (idea.trim()) {
      const formData = {
        idea: idea.trim(),
        niche: 'Custom Idea',
        subNiche: '',
        specificArea: ''
      };
      
      console.log('🚀 Idea Submission:', formData);
      
      onComplete(formData);
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
          className="px-6 py-2 bg-[#333333] hover:bg-[#444444] text-white rounded-[10px] transition-all"
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
      </div>
      
      <div className="max-w-2xl mx-auto">
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Describe your idea... What problem are you solving? Who is your target audience? What makes your solution unique?"
          className="w-full h-32 px-4 py-3 bg-[#222222] border border-[#444444] rounded-[10px] text-white placeholder-[#666666] focus:outline-none focus:ring-2 focus:ring-blue-500  resize-none"
        />
        
        <div className="mt-4 flex justify-center">
          <button
            onClick={handleIdeaSubmit}
            disabled={!idea.trim()}
            className="px-8 py-3 bg-white hover:bg-[#f0f0f0] disabled:bg-[#444444] text-[#121212] disabled:text-[#888888]  rounded-[10px] transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
          >
            Continue to Code
          </button>
        </div>
      </div>
    </div>
  );

  const renderNicheQuestions = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Let's find your niche!</h2>
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
              className={`p-4 rounded-[10px]  transition-all ${
                selectedNiche === key
                  ? 'bg-[#fff]  text-black'
                  : 'bg-[#222222] border-[#444444] text-[#cccccc] hover:border-[#555555] hover:text-white'
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
                className={`p-4 rounded-[10px]  transition-all ${
                  selectedSubNiche === key
                    ? 'bg-[#fff]  text-black'
                    : 'bg-[#222222]  text-[#cccccc] hover:border-[#555555] hover:text-white'
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
                className={`p-3 rounded-[10px]  transition-all ${
                  selectedArea === area
                    ? 'bg-[#fff] text-black'
                    : 'bg-[#222222]  text-[#cccccc] hover:border-[#555555] hover:text-white'
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
            className="px-8 py-3 bg-white hover:bg-[#f0f0f0] text-[#121212]  rounded-[10px] transition-all transform hover:scale-105"
          >
            Continue to Code
          </button>
        </div>
      )}
    </div>
  );

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
              onClick={() => setHasIdea(true)}
              className="px-8 py-4 bg-white hover:bg-[#f0f0f0] text-[#121212]  rounded-[10px] transition-all transform hover:scale-105"
            >
              Yes, I have an idea!
            </button>
            <button
              onClick={() => setHasIdea(false)}
              className="px-8 py-4 bg-[#333333] hover:bg-[#444444] text-white  rounded-[10px] transition-all transform hover:scale-105"
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
    </div>
  );
}

export default Brainstorm;
