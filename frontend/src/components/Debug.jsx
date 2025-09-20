import React, { useState, useEffect } from 'react';

// Mock debug issues and solutions
const DEBUG_ISSUES = [
  {
    id: 1,
    type: 'error',
    severity: 'high',
    title: 'Database Connection Failed',
    description: 'Unable to connect to the database. Check connection string and credentials.',
    solution: 'Verify database credentials and ensure the database server is running. Update connection string if needed.',
    code: 'const connection = await mongoose.connect(process.env.MONGODB_URI);',
    status: 'pending'
  },
  {
    id: 2,
    type: 'warning',
    severity: 'medium',
    title: 'Missing Input Validation',
    description: 'User input is not being validated before processing.',
    solution: 'Add input validation middleware to sanitize and validate user data.',
    code: 'const validateInput = (req, res, next) => { /* validation logic */ };',
    status: 'pending'
  },
  {
    id: 3,
    type: 'performance',
    severity: 'low',
    title: 'Slow Query Performance',
    description: 'Database queries are taking longer than expected.',
    solution: 'Add database indexes and optimize query structure.',
    code: 'db.collection.createIndex({ "field": 1 });',
    status: 'pending'
  },
  {
    id: 4,
    type: 'security',
    severity: 'high',
    title: 'Missing Authentication',
    description: 'API endpoints are not protected with authentication.',
    solution: 'Implement JWT authentication middleware for protected routes.',
    code: 'const authenticateToken = (req, res, next) => { /* auth logic */ };',
    status: 'pending'
  },
  {
    id: 5,
    type: 'error',
    severity: 'medium',
    title: 'CORS Configuration Missing',
    description: 'Cross-origin requests are being blocked.',
    solution: 'Configure CORS middleware to allow requests from frontend domain.',
    code: 'app.use(cors({ origin: process.env.FRONTEND_URL }));',
    status: 'pending'
  }
];

function Debug({ onComplete, projectData }) {
  const [totalIssues, setTotalIssues] = useState(0);
  const [isScanning, setIsScanning] = useState(false);
  const [isFixing, setIsFixing] = useState(false);
  const [fixedCount, setFixedCount] = useState(0);

  useEffect(() => {
    // Simulate code scanning
    scanCode();
  }, []);

  // Auto-proceed when no issues are found
  useEffect(() => {
    if (totalIssues === 0 && !isScanning && !isFixing) {
      const timer = setTimeout(() => {
        handleContinue();
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, [totalIssues, isScanning, isFixing]);

  const scanCode = async () => {
    setIsScanning(true);
    
    // Simulate scanning delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Randomly select 3-5 issues
    const issueCount = Math.floor(Math.random() * 3) + 3;
    setTotalIssues(issueCount);
    setIsScanning(false);
    
    // Start auto-fixing after scan completes
    setTimeout(() => {
      autoFixIssues(issueCount);
    }, 1000);
  };

  const autoFixIssues = async (count) => {
    setIsFixing(true);
    
    // Fix issues one by one with delay
    for (let i = 0; i < count; i++) {
      await new Promise(resolve => setTimeout(resolve, 800));
      setFixedCount(prev => prev + 1);
    }
    
    setIsFixing(false);
    
    // Auto-proceed to deploy after all issues are fixed
    setTimeout(() => {
      handleContinue();
    }, 2000);
  };

  const handleContinue = () => {
    onComplete({
      totalIssues: totalIssues,
      fixedCount: fixedCount,
      remainingCount: totalIssues - fixedCount
    });
  };


  return (
    <div className="max-w-4xl mx-auto space-y-8">


      {isScanning ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="relative">
            <div className="w-20 h-20 border-4 border-[#343434] border-t-white rounded-full animate-spin mb-6"></div>
          </div>
          <h3 className="text-2xl font-semibold text-white mb-2">Scanning Code...</h3>
        </div>
      ) : isFixing ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="relative mb-8">
            <div className="w-24 h-24 border-4 border-[#343434] border-t-white rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-white font-bold text-lg">{fixedCount}/{totalIssues}</div>
            </div>
          </div>
          <h3 className="text-2xl font-semibold text-white mb-2">Fixing Issues...</h3>
          <div className="mt-6 w-full max-w-md bg-[#343434] rounded-full h-2">
            <div 
              className="bg-white h-2 rounded-full transition-all duration-500"
              style={{ width: `${(fixedCount / totalIssues) * 100}%` }}
            ></div>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Results Summary */}
          <div className=" rounded-lg p-8 text-center">


            {fixedCount === totalIssues && totalIssues > 0 ? (
              <div className="space-y-4">
                <div className="text-6xl mb-4 font-bold text-white">✓</div>
                <h4 className="text-2xl font-semibold text-white mb-2">All Issues Resolved!</h4>
                <p className="text-[#888888] text-lg">Your code is now ready for deployment</p>
                <div className="mt-6">
                  <div className="inline-flex items-center space-x-2 px-6 py-3 bg-white text-[#121212] rounded-lg">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#121212]"></div>
                    <span className="font-semibold">Proceeding to deployment...</span>
                  </div>
                </div>
              </div>
            ) : totalIssues === 0 ? (
              <div className="space-y-4">
                <div className="text-6xl mb-4 font-bold text-white">✓</div>
                <h4 className="text-2xl font-semibold text-white mb-2">No Issues Found!</h4>
                <p className="text-[#888888] text-lg">Your code looks great! Ready to deploy.</p>
                <div className="mt-6">
                  <div className="inline-flex items-center space-x-2 px-6 py-3 bg-white text-[#121212] rounded-lg">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#121212]"></div>
                    <span className="font-semibold">Proceeding to deployment...</span>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

export default Debug;
