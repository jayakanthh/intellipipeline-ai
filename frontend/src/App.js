import React, { useState } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Navbar from './components/Navbar';
import DatasetUpload from './components/DatasetUpload';
import DatasetAnalysis from './components/DatasetAnalysis';
import PipelineViewer from './components/PipelineViewer';
import ModelResults from './components/ModelResults';
import Dashboard from './components/Dashboard';
import ApiDeployment from './components/ApiDeployment';

// Create a client
const queryClient = new QueryClient();

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [datasetId, setDatasetId] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [pipelineResults, setPipelineResults] = useState(null);
  const [modelResults, setModelResults] = useState(null);
  const [deploymentResults, setDeploymentResults] = useState(null);

  const steps = [
    { id: 0, title: 'Upload Dataset', component: DatasetUpload },
    { id: 1, title: 'Dataset Analysis', component: DatasetAnalysis },
    { id: 2, title: 'Pipeline Generation', component: PipelineViewer },
    { id: 3, title: 'Model Training', component: ModelResults },
    { id: 4, title: 'API Deployment', component: ApiDeployment },
    { id: 5, title: 'Dashboard', component: Dashboard }
  ];

  const CurrentComponent = steps[currentStep].component;

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App min-h-screen bg-base-200">
          <Navbar />
          
          {/* Progress Steps */}
          <div className="container mx-auto px-4 py-8">
            <ul className="steps steps-vertical lg:steps-horizontal w-full">
              {steps.map((step, index) => (
                <li
                  key={step.id} 
                  className={`step ${index <= currentStep ? 'step-primary' : ''}`}
                >
                  {step.title}
                </li>
              ))}
            </ul>
          </div>

          {/* Main Content */}
          <main className="container mx-auto px-4 pb-8">
            <CurrentComponent 
              datasetId={datasetId}
              setDatasetId={setDatasetId}
              analysisResults={analysisResults}
              setAnalysisResults={setAnalysisResults}
              pipelineResults={pipelineResults}
              setPipelineResults={setPipelineResults}
              modelResults={modelResults}
              setModelResults={setModelResults}
              deploymentResults={deploymentResults}
              setDeploymentResults={setDeploymentResults}
              currentStep={currentStep}
              setCurrentStep={setCurrentStep}
            />
          </main>

          {/* Navigation Buttons */}
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between">
              <button 
                className="btn btn-outline"
                onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                disabled={currentStep === 0}
              >
                Previous
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
                disabled={currentStep === steps.length - 1}
              >
                Next
              </button>
            </div>
          </div>

          <Toaster position="top-right" />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
