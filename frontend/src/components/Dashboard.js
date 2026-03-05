import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const Dashboard = ({ analysisResults, modelResults, deploymentResults }) => {
  
  const generateInsights = () => {
    const insights = [];
    
    if (analysisResults) {
      const quality = analysisResults.analysis.quality.data_quality_score;
      if (quality > 0.9) {
        insights.push({ type: 'success', message: 'Excellent data quality detected!' });
      } else if (quality > 0.7) {
        insights.push({ type: 'warning', message: 'Good data quality with minor issues.' });
      } else {
        insights.push({ type: 'error', message: 'Data quality needs improvement.' });
      }
    }
    
    if (modelResults) {
      const accuracy = modelResults.best_model.metrics.accuracy;
      if (accuracy > 0.9) {
        insights.push({ type: 'success', message: 'High model accuracy achieved!' });
      } else if (accuracy > 0.8) {
        insights.push({ type: 'info', message: 'Good model performance.' });
      }
    }
    
    if (deploymentResults) {
      insights.push({ type: 'success', message: 'Model successfully deployed to API!' });
    }
    
    return insights;
  };

  const insights = generateInsights();

  const getInsightColor = (type) => {
    switch (type) {
      case 'success': return 'alert-success';
      case 'warning': return 'alert-warning';
      case 'error': return 'alert-error';
      default: return 'alert-info';
    }
  };

  // Sample data for visualizations
  const performanceData = modelResults ? [
    { name: 'Accuracy', value: modelResults.best_model.metrics.accuracy },
    { name: 'Precision', value: modelResults.best_model.metrics.precision },
    { name: 'Recall', value: modelResults.best_model.metrics.recall },
    { name: 'F1-Score', value: modelResults.best_model.metrics.f1 }
  ] : [];

  const featureImportanceData = modelResults ? 
    modelResults.explanations.feature_importance.slice(0, 6) : [];

  const pipelineSteps = [
    { step: 'Data Upload', status: 'completed', icon: '📊' },
    { step: 'Analysis', status: 'completed', icon: '🔍' },
    { step: 'Pipeline', status: 'completed', icon: '⚙️' },
    { step: 'Training', status: 'completed', icon: '🤖' },
    { step: 'Deployment', status: 'completed', icon: '🚀' }
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">📊 AI Data Engineer Dashboard</h1>
        <p className="text-lg text-gray-600">
          Complete overview of your automated ML pipeline
        </p>
      </div>

      {/* Insights */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {insights.map((insight, index) => (
          <div key={index} className={`alert ${getInsightColor(insight.type)}`}>
            <span>{insight.message}</span>
          </div>
        ))}
      </div>

      {/* Pipeline Progress */}
      <div className="card bg-base-100 shadow-xl mb-8">
        <div className="card-body">
          <h2 className="card-title mb-4">🔄 Pipeline Progress</h2>
          <div className="steps steps-horizontal w-full">
            {pipelineSteps.map((step, index) => (
              <div key={index} className="step step-primary">
                <div className="step-content">
                  <div className="text-2xl mb-2">{step.icon}</div>
                  <div className="step-title text-sm">{step.step}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card bg-primary text-primary-content">
          <div className="card-body">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="card-title text-lg">Model Accuracy</h3>
                <p className="text-3xl font-bold">
                  {modelResults ? (modelResults.best_model.metrics.accuracy * 100).toFixed(1) : '0.0'}%
                </p>
              </div>
              <div className="text-4xl">🎯</div>
            </div>
          </div>
        </div>

        <div className="card bg-secondary text-secondary-content">
          <div className="card-body">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="card-title text-lg">API Status</h3>
                <p className="text-3xl font-bold">
                  {deploymentResults ? 'Active' : 'Inactive'}
                </p>
              </div>
              <div className="text-4xl">🚀</div>
            </div>
          </div>
        </div>

        <div className="card bg-accent text-accent-content">
          <div className="card-body">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="card-title text-lg">Training Time</h3>
                <p className="text-3xl font-bold">2.3m</p>
              </div>
              <div className="text-4xl">⏱️</div>
            </div>
          </div>
        </div>

        <div className="card bg-neutral text-neutral-content">
          <div className="card-body">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="card-title text-lg">Data Quality</h3>
                <p className="text-3xl font-bold">
                  {analysisResults ? (analysisResults.analysis.quality.data_quality_score * 100).toFixed(0) : '0'}%
                </p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8 mb-8">
        {/* Model Performance */}
        {modelResults && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h3 className="card-title">📈 Model Performance Metrics</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={performanceData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="name" />
                    <PolarRadiusAxis angle={90} domain={[0, 1]} />
                    <Radar
                      name="Performance"
                      dataKey="value"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.6}
                    />
                    <Tooltip formatter={(value) => [(value * 100).toFixed(1) + '%', 'Score']} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Feature Importance */}
        {modelResults && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h3 className="card-title">🔍 Feature Importance</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={featureImportanceData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="feature" type="category" width={80} />
                    <Tooltip formatter={(value) => [(value * 100).toFixed(1) + '%', 'Importance']} />
                    <Bar dataKey="importance" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* API Usage Stats */}
      {deploymentResults && (
        <div className="card bg-base-100 shadow-xl mb-8">
          <div className="card-body">
            <h3 className="card-title">📡 API Usage Statistics</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">127</div>
                <div className="text-sm text-gray-600">Total Requests</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-secondary">98.4%</div>
                <div className="text-sm text-gray-600">Success Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-accent">142ms</div>
                <div className="text-sm text-gray-600">Avg Response Time</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h3 className="card-title">⚡ Quick Actions</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="btn btn-primary">
              📊 Download Report
            </button>
            <button className="btn btn-secondary">
              🔧 Retrain Model
            </button>
            <button className="btn btn-accent">
              📈 Monitor API
            </button>
            <button className="btn btn-info">
              🚀 Deploy New Model
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;