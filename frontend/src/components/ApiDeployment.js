import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const ApiDeployment = ({ modelResults, deploymentResults, setDeploymentResults, setCurrentStep }) => {
  const [deploying, setDeploying] = useState(false);
  const [progress, setProgress] = useState(0);

  const deployModel = async () => {
    setDeploying(true);
    setProgress(0);

    // Simulate deployment progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 20;
      });
    }, 1000);

    // Simulate deployment completion
    setTimeout(() => {
      const mockDeployment = {
        api_endpoint: "http://localhost:8000/predict",
        api_key: "demo-key-12345",
        model_name: modelResults.best_model.name,
        deployment_status: "active",
        swagger_docs: "http://localhost:8000/docs",
        example_request: {
          method: "POST",
          url: "http://localhost:8000/predict",
          headers: {
            "Content-Type": "application/json",
            "X-API-Key": "demo-key-12345"
          },
          body: {
            age: 35,
            income: 75000,
            spending_score: 0.8,
            category_encoded: 1
          }
        },
        example_response: {
          prediction: "high_value",
          confidence: 0.92,
          model_name: "XGBClassifier",
          timestamp: new Date().toISOString()
        }
      };

      setDeploymentResults(mockDeployment);
      setDeploying(false);
      toast.success('Model deployed successfully!');
    }, 5000);
  };

  const testApi = async () => {
    try {
      const response = await axios.post(deploymentResults.api_endpoint, 
        deploymentResults.example_request.body,
        {
          headers: deploymentResults.example_request.headers
        }
      );
      
      toast.success('API test successful!');
      console.log('API Response:', response.data);
    } catch (error) {
      toast.error('API test failed: ' + error.message);
    }
  };

  if (deploying || !deploymentResults) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🚀</div>
          <h2 className="text-2xl font-bold mb-4">Deploying Model API</h2>
          <p className="text-gray-600">
            Generating API endpoints and deployment configuration...
          </p>
        </div>

        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Deployment Progress</span>
              <span className="text-sm text-gray-500">{progress}%</span>
            </div>
            <progress className="progress progress-primary w-full" value={progress} max="100"></progress>
            
            <div className="mt-4 space-y-2">
              <div className="flex items-center space-x-2">
                <span className={`loading loading-spinner loading-sm ${progress >= 20 ? 'text-primary' : ''}`}></span>
                <span>Generating API code...</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`loading loading-spinner loading-sm ${progress >= 40 ? 'text-primary' : ''}`}></span>
                <span>Creating Docker configuration...</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`loading loading-spinner loading-sm ${progress >= 60 ? 'text-primary' : ''}`}></span>
                <span>Setting up authentication...</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`loading loading-spinner loading-sm ${progress >= 80 ? 'text-primary' : ''}`}></span>
                <span>Deploying to server...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const { api_endpoint, api_key, deployment_status, swagger_docs, example_request, example_response } = deploymentResults;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">🎉</div>
        <h2 className="text-2xl font-bold mb-4">Model API Deployed!</h2>
        <p className="text-gray-600">
          Your trained model is now available as a REST API endpoint
        </p>
      </div>

      {/* API Status */}
      <div className="card bg-success text-success-content mb-8">
        <div className="card-body">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="card-title">🟢 API Status: Active</h3>
              <p>Your model is successfully deployed and ready for predictions</p>
            </div>
            <div className="text-right">
              <div className="text-sm opacity-75">Model</div>
              <div className="font-semibold">{modelResults.best_model.name}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* API Endpoint */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title">🔗 API Endpoint</h3>
            <div className="space-y-4">
              <div>
                <label className="label">
                  <span className="label-text">Endpoint URL</span>
                </label>
                <div className="input-group">
                  <input type="text" className="input input-bordered w-full" value={api_endpoint} readOnly />
                  <button className="btn btn-square" onClick={() => navigator.clipboard.writeText(api_endpoint)}>
                    📋
                  </button>
                </div>
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">API Key</span>
                </label>
                <div className="input-group">
                  <input type="text" className="input input-bordered w-full" value={api_key} readOnly />
                  <button className="btn btn-square" onClick={() => navigator.clipboard.writeText(api_key)}>
                    📋
                  </button>
                </div>
              </div>

              <div>
                <a href={swagger_docs} target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm">
                  📚 View API Documentation
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Test API */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title">🧪 Test Your API</h3>
            <p className="text-gray-600 mb-4">
              Send a test request to verify your API is working correctly
            </p>
            <button className="btn btn-primary" onClick={testApi}>
              Test API Now
            </button>
          </div>
        </div>
      </div>

      {/* API Usage Examples */}
      <div className="card bg-base-100 shadow-xl mb-8">
        <div className="card-body">
          <h3 className="card-title">💻 API Usage Examples</h3>
          
          <div className="tabs tabs-boxed mb-4">
            <input type="radio" name="api_tabs" className="tab" aria-label="cURL" defaultChecked />
            <input type="radio" name="api_tabs" className="tab" aria-label="Python" />
            <input type="radio" name="api_tabs" className="tab" aria-label="JavaScript" />
          </div>

          {/* cURL Example */}
          <div className="mockup-code mb-4">
            <pre data-prefix="$"><code>curl -X POST {api_endpoint} \</code></pre>
            <pre data-prefix=">"><code>  -H "Content-Type: application/json" \</code></pre>
            <pre data-prefix=">"><code>  -H "X-API-Key: {api_key}" \</code></pre>
            <pre data-prefix=">"><code>  -d '{JSON.stringify(example_request.body, null, 2)}'</code></pre>
          </div>

          {/* Example Response */}
          <div className="alert alert-success">
            <div className="font-semibold mb-2">Example Response:</div>
            <pre className="text-sm"><code>{JSON.stringify(example_response, null, 2)}</code></pre>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button 
          className="btn btn-primary btn-lg"
          onClick={() => setCurrentStep(5)}
        >
          View Dashboard →
        </button>
        <button 
          className="btn btn-outline btn-lg"
          onClick={() => setCurrentStep(3)}
        >
          Back to Model Results
        </button>
        <button 
          className="btn btn-secondary btn-lg"
          onClick={deployModel}
        >
          Redeploy Model
        </button>
      </div>
    </div>
  );
};

export default ApiDeployment;