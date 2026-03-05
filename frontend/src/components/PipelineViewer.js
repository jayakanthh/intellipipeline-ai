import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const PipelineViewer = ({ analysisResults, pipelineResults, setPipelineResults, setCurrentStep }) => {
  
  const generatePipeline = async () => {
    // This would typically call your backend API
    // For now, we'll simulate the pipeline generation
    const mockPipeline = {
      cleaning_steps: [
        {
          step: "remove_duplicates",
          reason: "Found 150 duplicate rows in the dataset"
        },
        {
          step: "handle_missing_values",
          columns: ["age", "income"],
          method: "median_imputation",
          reason: "Numerical columns with 5% missing values"
        }
      ],
      feature_engineering: [
        {
          step: "one_hot_encode",
          columns: ["category", "region"],
          reason: "Categorical variables need encoding for ML models"
        },
        {
          step: "scale_features",
          columns: ["age", "income", "spending_score"],
          method: "standard_scaler",
          reason: "Numerical features need scaling for optimal model performance"
        }
      ],
      model_training: {
        models: [
          {
            name: "RandomForestClassifier",
            params: { n_estimators: 100, max_depth: 10 },
            reason: "Ensemble method good for tabular data with feature importance"
          },
          {
            name: "XGBClassifier",
            params: { n_estimators: 100, learning_rate: 0.1 },
            reason: "Gradient boosting for high performance on structured data"
          }
        ]
      },
      generated_code: `import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

class AutoMLPipeline:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def clean_data(self, df):
        """Clean the dataset"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
        
        return df
    
    def engineer_features(self, X, y=None):
        """Engineer features"""
        # One-hot encode categorical variables
        categorical_cols = X.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
        
        # Scale numerical features
        numerical_cols = X.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            X[numerical_cols] = self.scaler.fit_transform(X[numerical_cols])
        
        return X
    
    def train_model(self, X, y):
        """Train the model"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        return accuracy, self.model

# Usage
pipeline = AutoMLPipeline()
cleaned_data = pipeline.clean_data(df)
X_processed = pipeline.engineer_features(cleaned_data.drop('target', axis=1))
accuracy, model = pipeline.train_model(X_processed, cleaned_data['target'])`
    };

    setPipelineResults(mockPipeline);
  };

  if (!pipelineResults) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">⚙️</div>
          <h2 className="text-2xl font-bold mb-4">Generate ML Pipeline</h2>
          <p className="text-gray-600">
            Our AI will generate a complete machine learning pipeline based on your dataset analysis
          </p>
        </div>

        <div className="card bg-base-100 shadow-xl">
          <div className="card-body text-center">
            <h3 className="card-title justify-center">Ready to Generate Pipeline</h3>
            <p className="mb-6">
              Based on the dataset analysis, we're ready to create an automated ML pipeline 
              with data cleaning, feature engineering, and model selection.
            </p>
            <button className="btn btn-primary btn-lg" onClick={generatePipeline}>
              Generate Pipeline
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { cleaning_steps, feature_engineering, model_training, generated_code } = pipelineResults;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">⚙️</div>
        <h2 className="text-2xl font-bold mb-4">Generated ML Pipeline</h2>
        <p className="text-gray-600">
          Complete pipeline generated by our AI based on your dataset analysis
        </p>
      </div>

      {/* Pipeline Steps */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {/* Data Cleaning */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title">🧹 Data Cleaning</h3>
            <div className="space-y-3">
              {cleaning_steps.map((step, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="font-semibold">{step.step.replace('_', ' ').toUpperCase()}</div>
                  <div className="text-sm text-gray-600 mt-1">{step.reason}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Feature Engineering */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title">🔧 Feature Engineering</h3>
            <div className="space-y-3">
              {feature_engineering.map((step, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="font-semibold">{step.step.replace('_', ' ').toUpperCase()}</div>
                  <div className="text-sm text-gray-600 mt-1">{step.reason}</div>
                  {step.columns && (
                    <div className="text-xs text-gray-500 mt-1">
                      Columns: {step.columns.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Model Training */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title">🤖 Model Training</h3>
            <div className="space-y-3">
              {model_training.models.map((model, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="font-semibold">{model.name}</div>
                  <div className="text-sm text-gray-600 mt-1">{model.reason}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    Params: {JSON.stringify(model.params)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Generated Code */}
      <div className="card bg-base-100 shadow-xl mb-8">
        <div className="card-body">
          <h3 className="card-title">💻 Generated Pipeline Code</h3>
          <p className="text-gray-600 mb-4">
            Complete Python code for your ML pipeline, ready to use:
          </p>
          <div className="mockup-code">
            <SyntaxHighlighter language="python" style={tomorrow}>
              {generated_code}
            </SyntaxHighlighter>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button 
          className="btn btn-primary btn-lg"
          onClick={() => setCurrentStep(3)}
        >
          Train Models →
        </button>
        <button 
          className="btn btn-outline btn-lg"
          onClick={() => setCurrentStep(1)}
        >
          Back to Analysis
        </button>
      </div>
    </div>
  );
};

export default PipelineViewer;