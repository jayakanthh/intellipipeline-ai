import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const DatasetAnalysis = ({ datasetId, analysisResults, setAnalysisResults, setCurrentStep }) => {
  const [loading, setLoading] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [targetColumn, setTargetColumn] = useState('');
  const [taskType, setTaskType] = useState('classification');

  useEffect(() => {
    if (datasetId && !analysisResults) {
      startAnalysis();
    }
  }, [datasetId]);

  useEffect(() => {
    if (taskId) {
      const interval = setInterval(checkAnalysisStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [taskId]);

  const startAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`/api/analyze-dataset/${datasetId}`, {
        target_column: targetColumn,
        task_type: taskType
      });
      
      if (response.data.task_id) {
        setTaskId(response.data.task_id);
        toast.success('Dataset analysis started!');
      }
    } catch (error) {
      toast.error('Failed to start analysis: ' + error.message);
      setLoading(false);
    }
  };

  const checkAnalysisStatus = async () => {
    try {
      const response = await axios.get(`/api/task-status/${taskId}`);
      
      if (response.data.status === 'completed') {
        setAnalysisResults(response.data.result);
        setLoading(false);
        toast.success('Dataset analysis completed!');
      }
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  if (loading || !analysisResults) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h2 className="text-2xl font-bold mb-4">Analyzing Your Dataset</h2>
          <div className="flex justify-center">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
          <p className="mt-4 text-gray-600">
            Our AI is analyzing your dataset for quality, patterns, and insights...
          </p>
        </div>
      </div>
    );
  }

  const { basic_stats, quality, columns, correlations, target_suggestions } = analysisResults.analysis;

  const qualityData = [
    { name: 'Complete', value: quality.data_quality_score * 100 },
    { name: 'Issues', value: (1 - quality.data_quality_score) * 100 }
  ];

  const COLORS = ['#10b981', '#ef4444'];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">Dataset Analysis Results</h1>
        <p className="text-lg text-gray-600">
          Comprehensive analysis of your dataset with AI-powered insights
        </p>
      </div>

      {/* Basic Statistics */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="card bg-primary text-primary-content">
          <div className="card-body">
            <h3 className="card-title">Rows</h3>
            <p className="text-3xl font-bold">{basic_stats.rows.toLocaleString()}</p>
          </div>
        </div>
        <div className="card bg-secondary text-secondary-content">
          <div className="card-body">
            <h3 className="card-title">Columns</h3>
            <p className="text-3xl font-bold">{basic_stats.columns}</p>
          </div>
        </div>
        <div className="card bg-accent text-accent-content">
          <div className="card-body">
            <h3 className="card-title">Memory Usage</h3>
            <p className="text-3xl font-bold">{basic_stats.memory_usage_mb.toFixed(1)} MB</p>
          </div>
        </div>
        <div className="card bg-neutral text-neutral-content">
          <div className="card-body">
            <h3 className="card-title">Quality Score</h3>
            <p className="text-3xl font-bold">{(quality.data_quality_score * 100).toFixed(0)}%</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Data Quality */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">Data Quality Assessment</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={qualityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {qualityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="mt-4 space-y-2">
              <div className="flex justify-between">
                <span>Missing Values:</span>
                <span className="font-semibold">{quality.missing_values.total_missing}</span>
              </div>
              <div className="flex justify-between">
                <span>Duplicate Rows:</span>
                <span className="font-semibold">{quality.duplicates.duplicate_rows}</span>
              </div>
              <div className="flex justify-between">
                <span>Missing Percentage:</span>
                <span className="font-semibold">{quality.missing_values.missing_percentage.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Target Suggestions */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">🎯 Target Variable Suggestions</h2>
            {target_suggestions && target_suggestions.length > 0 ? (
              <div className="space-y-3">
                {target_suggestions.slice(0, 5).map((suggestion, index) => (
                  <div key={index} className="border rounded-lg p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold">{suggestion.column}</span>
                      <div className="badge badge-primary">{suggestion.type}</div>
                    </div>
                    <div className="text-sm text-gray-600">
                      Score: {suggestion.score}/5
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {suggestion.reasons.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No clear target variable suggestions found.</p>
            )}
          </div>
        </div>
      </div>

      {/* Column Analysis */}
      <div className="card bg-base-100 shadow-xl mb-8">
        <div className="card-body">
          <h2 className="card-title">📊 Column Analysis</h2>
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              <thead>
                <tr>
                  <th>Column</th>
                  <th>Type</th>
                  <th>Unique Values</th>
                  <th>Missing %</th>
                  <th>Quality</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(columns).slice(0, 10).map(([colName, colData]) => (
                  <tr key={colName}>
                    <td className="font-medium">{colName}</td>
                    <td>
                      <div className="badge badge-outline">{colData.type}</div>
                    </td>
                    <td>{colData.unique_values}</td>
                    <td>{colData.null_percentage.toFixed(1)}%</td>
                    <td>
                      <div className={`badge ${
                        colData.null_percentage < 5 ? 'badge-success' : 
                        colData.null_percentage < 20 ? 'badge-warning' : 'badge-error'
                      }`}>
                        {colData.null_percentage < 5 ? 'Good' : 
                         colData.null_percentage < 20 ? 'Fair' : 'Poor'}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button 
          className="btn btn-primary btn-lg"
          onClick={() => setCurrentStep(2)}
        >
          Generate Pipeline →
        </button>
        <button 
          className="btn btn-outline btn-lg"
          onClick={() => setCurrentStep(0)}
        >
          Upload New Dataset
        </button>
      </div>
    </div>
  );
};

export default DatasetAnalysis;