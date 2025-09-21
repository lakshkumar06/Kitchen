import React, { useState, useEffect } from 'react';

// Mock deployment platforms and configurations
const DEPLOYMENT_PLATFORMS = {
  vercel: {
    name: 'Vercel',
    icon: 'V',
    description: 'Perfect for React/Next.js applications',
    features: ['Automatic deployments', 'Edge functions', 'Analytics'],
    pricing: 'Free tier available'
  },
  netlify: {
    name: 'Netlify',
    icon: 'N',
    description: 'Great for static sites and JAMstack',
    features: ['Form handling', 'Serverless functions', 'Split testing'],
    pricing: 'Free tier available'
  },
  heroku: {
    name: 'Heroku',
    icon: 'H',
    description: 'Simple deployment for full-stack apps',
    features: ['Easy scaling', 'Add-ons marketplace', 'Git integration'],
    pricing: 'Paid plans only'
  },
  aws: {
    name: 'AWS',
    icon: 'A',
    description: 'Enterprise-grade cloud platform',
    features: ['High scalability', 'Multiple services', 'Global infrastructure'],
    pricing: 'Pay-as-you-go'
  },
  digitalocean: {
    name: 'DigitalOcean',
    icon: 'D',
    description: 'Developer-friendly cloud platform',
    features: ['Simple pricing', 'Droplets', 'Managed databases'],
    pricing: 'Starting at $5/month'
  }
};

function Deploy({ onComplete, projectData }) {
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [deploymentConfig, setDeploymentConfig] = useState({
    domain: '',
    environment: 'production',
    buildCommand: 'npm run build',
    outputDirectory: 'dist'
  });
  const [isDeploying, setIsDeploying] = useState(false);
  const [deploymentStatus, setDeploymentStatus] = useState('pending');
  const [deploymentLogs, setDeploymentLogs] = useState([]);

  const addLog = (message, type = 'info') => {
    setDeploymentLogs(prev => [...prev, { message, type, timestamp: new Date() }]);
  };

  const simulateDeployment = async () => {
    setIsDeploying(true);
    setDeploymentStatus('deploying');
    
    const steps = [
      { message: 'Initializing deployment...' },
      { message: 'Installing dependencies...' },
      { message: 'Building application...' },
      { message: 'Running tests...' },
      { message: 'Uploading files...' },
      { message: 'Configuring environment...' },
      { message: 'Deployment successful! 🎉' }
    ];

    for (const step of steps) {
      addLog(step.message, step.message.includes('successful') ? 'success' : 'info');
    }

    setDeploymentStatus('success');
    setIsDeploying(false);
  };

  const handleDeploy = () => {
    if (!selectedPlatform) return;
    simulateDeployment();
  };

  const handleComplete = () => {
    onComplete({
      deploymentStatus,
      platform: selectedPlatform,
      config: deploymentConfig,
      logs: deploymentLogs
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'text-green-400';
      case 'deploying': return 'text-yellow-400';
      case 'failed': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      default: return 'text-white/70';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Deploy Your Application</h2>
        <p className="text-[#888888] text-lg">Choose a platform and deploy your {projectData.specificArea || 'application'}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Selection */}
        <div className="space-y-6">
          <div className="bg-[#222222] rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Choose Deployment Platform</h3>
            <div className="space-y-3">
              {Object.entries(DEPLOYMENT_PLATFORMS).map(([key, platform]) => (
                <button
                  key={key}
                  onClick={() => setSelectedPlatform(key)}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    selectedPlatform === key
                      ? 'bg-[#1e40af] border-[#3b82f6]'
                      : 'bg-[#333333] border-[#444444] hover:border-[#555555]'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl font-bold text-[#888888]">{platform.icon}</div>
                    <div className="flex-1">
                      <div className="font-semibold text-white">{platform.name}</div>
                      <div className="text-sm text-[#888888]">{platform.description}</div>
                      <div className="text-xs mt-1 text-[#666666]">{platform.pricing}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Deployment Configuration */}
          {selectedPlatform && (
            <div className="bg-[#222222] rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Deployment Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#cccccc] mb-2">Domain Name</label>
                  <input
                    type="text"
                    value={deploymentConfig.domain}
                    onChange={(e) => setDeploymentConfig(prev => ({ ...prev, domain: e.target.value }))}
                    placeholder="my-app.vercel.app"
                    className="w-full px-3 py-2 bg-[#333333] border border-[#444444] rounded-lg text-white placeholder-[#666666] focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-[#cccccc] mb-2">Environment</label>
                  <select
                    value={deploymentConfig.environment}
                    onChange={(e) => setDeploymentConfig(prev => ({ ...prev, environment: e.target.value }))}
                    className="w-full px-3 py-2 bg-[#333333] border border-[#444444] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="production">Production</option>
                    <option value="staging">Staging</option>
                    <option value="development">Development</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#cccccc] mb-2">Build Command</label>
                  <input
                    type="text"
                    value={deploymentConfig.buildCommand}
                    onChange={(e) => setDeploymentConfig(prev => ({ ...prev, buildCommand: e.target.value }))}
                    className="w-full px-3 py-2 bg-[#333333] border border-[#444444] rounded-lg text-white placeholder-[#666666] focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Deployment Status and Logs */}
        <div className="space-y-6">
          {/* Deployment Status */}
          <div className="bg-[#222222] rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Deployment Status</h3>
            
            {deploymentStatus === 'pending' && (
              <div className="text-center py-8">
                <div className="text-6xl mb-4 font-bold text-[#888888]">→</div>
                <p className="text-[#888888]">Ready to deploy your application</p>
              </div>
            )}

            {deploymentStatus === 'deploying' && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-yellow-400 font-semibold">Deploying to {DEPLOYMENT_PLATFORMS[selectedPlatform]?.name}...</p>
              </div>
            )}

            {deploymentStatus === 'success' && (
              <div className="text-center py-8">
                <div className="text-6xl mb-4 font-bold text-green-400">✓</div>
                <h4 className="text-xl font-semibold text-green-400 mb-2">Deployment Successful!</h4>
                <p className="text-[#888888] mb-4">Your application is now live</p>
                <div className="bg-[#0a4a0a] rounded-lg p-4">
                  <p className="text-green-300 font-mono">
                    https://{deploymentConfig.domain || 'your-app.vercel.app'}
                  </p>
                </div>
              </div>
            )}

            {deploymentStatus === 'failed' && (
              <div className="text-center py-8">
                <div className="text-6xl mb-4 font-bold text-red-400">✗</div>
                <h4 className="text-xl font-semibold text-red-400 mb-2">Deployment Failed</h4>
                <p className="text-[#888888]">Please check the logs and try again</p>
              </div>
            )}
          </div>

          {/* Deployment Logs */}
          {deploymentLogs.length > 0 && (
            <div className="bg-[#222222] rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Deployment Logs</h3>
              <div className="bg-[#121212] rounded-lg p-4 max-h-64 overflow-y-auto">
                {deploymentLogs.map((log, index) => (
                  <div key={index} className="flex items-start space-x-3 py-1">
                    <span className="text-xs font-mono text-[#666666]">
                      {log.timestamp.toLocaleTimeString()}
                    </span>
                    <span className={`text-sm font-mono ${getLogColor(log.type)}`}>
                      {log.message}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        {deploymentStatus === 'pending' && (
          <button
            onClick={handleDeploy}
            disabled={!selectedPlatform}
            className={`px-8 py-3 font-semibold rounded-lg transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed ${
              selectedPlatform 
                ? 'bg-white hover:bg-[#f0f0f0] text-[#121212]' 
                : 'bg-[#444444] text-[#888888]'
            }`}
          >
            Deploy Now
          </button>
        )}
        
        {deploymentStatus === 'success' && (
          <button
            onClick={handleComplete}
            className="px-8 py-3 bg-white hover:bg-[#f0f0f0] text-[#121212] font-semibold rounded-lg transition-all transform hover:scale-105"
          >
            Complete Workflow
          </button>
        )}
      </div>
    </div>
  );
}

export default Deploy;
