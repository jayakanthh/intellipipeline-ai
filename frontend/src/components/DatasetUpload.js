import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import toast from 'react-hot-toast';

const DatasetUpload = ({ setDatasetId, setCurrentStep }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const validTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/json'];
    if (!validTypes.includes(file.type)) {
      toast.error('Please upload a CSV, Excel, or JSON file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await axios.post('/api/upload-dataset', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });

      if (response.data.file_id) {
        setDatasetId(response.data.file_id);
        toast.success('Dataset uploaded successfully!');
        setCurrentStep(1); // Move to analysis step
      }
    } catch (error) {
      toast.error('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [setDatasetId, setCurrentStep]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
    },
    maxFiles: 1,
  });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">AI Data Engineer Agent</h1>
        <p className="text-lg text-gray-600">
          Upload your dataset and let our AI automatically analyze, clean, engineer features, 
          train models, and deploy APIs. No coding required!
        </p>
      </div>

      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title">Upload Your Dataset</h2>
          
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-primary'
            }`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center space-y-4">
              <div className="text-6xl">📊</div>
              <div>
                {isDragActive ? (
                  <p className="text-lg font-medium">Drop the file here...</p>
                ) : (
                  <>
                    <p className="text-lg font-medium">Drag & drop your dataset here</p>
                    <p className="text-sm text-gray-500 mt-2">
                      or click to select a file (CSV, Excel, JSON)
                    </p>
                  </>
                )}
              </div>
              
              <div className="text-sm text-gray-400">
                Supported formats: CSV, Excel (.xlsx), JSON
              </div>
            </div>
          </div>

          {uploading && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Uploading...</span>
                <span className="text-sm text-gray-500">{uploadProgress}%</span>
              </div>
              <progress className="progress progress-primary w-full" value={uploadProgress} max="100"></progress>
            </div>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mt-12">
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body items-center text-center">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="card-title">AI-Powered Analysis</h3>
            <p>Automatic dataset profiling and quality assessment</p>
          </div>
        </div>

        <div className="card bg-base-100 shadow-lg">
          <div className="card-body items-center text-center">
            <div className="text-4xl mb-4">⚙️</div>
            <h3 className="card-title">Auto Pipeline Generation</h3>
            <p>Intelligent data cleaning and feature engineering</p>
          </div>
        </div>

        <div className="card bg-base-100 shadow-lg">
          <div className="card-body items-center text-center">
            <div className="text-4xl mb-4">🚀</div>
            <h3 className="card-title">Model & API Deployment</h3>
            <p>Automatic model training and API generation</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DatasetUpload;