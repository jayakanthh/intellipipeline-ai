import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const ModelResults = ({ analysisResults, modelResults, setModelResults, setCurrentStep }) => {
  const [training, setTraining] = useState(false);
  const [progress, setProgress] = useState(0);

  const startTraining = async () => {
    setTraining(true);
    setProgress(0);

    // Simulate training progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 500);

    // Simulate training completion
    setTimeout(() => {
      const mockResults = {
        best_model: {
          name: "XGBClassifier",
          metrics: {
            accuracy: 0.924,
            precision: 0.916,
            recall: 0.928,
            f1: 0.922
          },
          cv_score: 0.918,
          description: "Gradient boosting classifier with excellent performance"
        },
        all_models: {
          "RandomForestClassifier": {
            metrics: { accuracy: 0.891, precision: 0.885, recall: 0.894, f1: 0.889 },
            cv_score: 0.885
          },
          "XGBClassifier": {
            metrics: { accuracy: 0.924, precision: 0.916, recall: 0.928, f1: 0.922 },
            cv_score: 0.918
          },
          "LogisticRegression": {
            metrics: { accuracy: 0.856, precision: 0.852, recall: 0.859, f1: 0.855 },
            cv_score: 0.851
          }
        },
        explanations: {
          feature_importance: [
            { feature: "income", importance: 0.342 },
            { feature: "age", importance: 0.289 },
            { feature: "spending_score", importance: 0.187 },
            { feature: "category_encoded", importance: 0.182 }
          ]
        }
      };

      setModelResults(mockResults);
      setTraining(false);
    }, 5000);
  };

  if (training || !modelResults) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🤖</div>
          <h2 className="text-2xl font-bold mb-4">Training ML Models</h2>
          <p className="text-gray-600">
            Our AI is training multiple models and selecting the best performer...
          </p>
        </div>

        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Training Progress</span>
              <span className="text-sm text-gray-500">{progress}%</span>
            </div>
            <progress className="progress progress-primary w-full" value={progress} max="100"></progress>
            
            <div className="mt-4">
              <div className="flex items-center space-x-2">
                <span className="loading loading-spinner loading-sm"></span>
                <span>Training RandomForestClassifier...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const { best_model, all_models, explanations } = modelResults;

  // Prepare data for charts
  const modelComparisonData = Object.entries(all_models).map(([name, data]) => ({
    name: name.replace('Classifier', '').replace('Regressor', ''),
    accuracy: data.metrics.accuracy,
    cv_score: data.cv_score
  }));

  const featureImportanceData = explanations.feature_importance.slice(0, 8);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">🏆</div>
        <h2 className="text-2xl font-bold mb-4">Model Training Results</h2>
        <p className="text-gray-600">
          Best model selected with performance metrics and insights
        </p>
      </div>

      {/* Best Model Card */}
      <div className="card bg-gradient-to-r from-primary to-secondary text-primary-content mb-8">
        <div className="card-body">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="card-title text-2xl">🥇 Best Model</h3>
              <p className="text-lg opacity-90">{best_model.name}</p>
              <p className="text-sm opacity-75">{best_model.description}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">{(best_model.metrics.accuracy * 100).toFixed(1)}%</div>
              <div className="text-sm opacity-75">Accuracy</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Model Comparison */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title">📈 Model Performance Comparison</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={modelComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0.8, 1.0]} />
                  <Tooltip formatter={(value) => [(value * 100).toFixed(1) + '%', 'Score']} />
                  <Bar dataKey="accuracy" fill="#3b82f6" name="Test Accuracy" />
                  <Bar dataKey="cv_score" fill="#10b981" name="CV Score" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title">📊 Performance Metrics</h3>
            <div className="space-y-4">
              {Object.entries(best_model.metrics).map(([metric, value]) => (
                <div key={metric} className="flex justify-between items-center">
                  <span className="font-medium capitalize">{metric}:</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full" 
                        style={{ width: `${value * 100}%` }}
                      ></div>
                    </div>
                    <span className="font-semibold">{(value * 100).toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Feature Importance */}
      <div className="card bg-base-100 shadow-xl mb-8">
        <div className="card-body">
          <h3 className="card-title">🔍 Feature Importance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureImportanceData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="feature" type="category" width={100} />
                <Tooltip formatter={(value) => [(value * 100).toFixed(1) + '%', 'Importance']} />
                <Bar dataKey="importance" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button 
          className="btn btn-primary btn-lg"
          onClick={() => setCurrentStep(4)}
        >
          Deploy API →
        </button>
        <button 
          className="btn btn-outline btn-lg"
          onClick={() => setCurrentStep(2)}
        >
          Back to Pipeline
        </button>
        <button 
          className="btn btn-secondary btn-lg"
          onClick={startTraining}
        >
          Retrain Models
        </button>
      </div>
    </div>
  );
};

export default ModelResults;