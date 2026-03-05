import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class ModelAPI:
    """Model API wrapper for deployment"""
    
    def __init__(self, model_path: str, model_info: Dict[str, Any], feature_names: List[str]):
        self.model = joblib.load(model_path)
        self.model_info = model_info
        self.feature_names = feature_names
        self.app = FastAPI(title="AI Model API", version="1.0.0")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "AI Model API",
                "model_name": self.model_info.get("name", "unknown"),
                "task_type": self.model_info.get("task_type", "unknown"),
                "version": "1.0.0"
            }
        
        @self.app.get("/model-info")
        async def get_model_info():
            return {
                "model_info": self.model_info,
                "feature_names": self.feature_names,
                "expected_input_format": "JSON with feature names as keys"
            }
        
        @self.app.post("/predict")
        async def predict(input_data: Dict[str, Any]):
            try:
                # Convert input to DataFrame
                input_df = pd.DataFrame([input_data])
                
                # Ensure all required features are present
                missing_features = set(self.feature_names) - set(input_df.columns)
                if missing_features:
                    raise HTTPException(status_code=400, detail=f"Missing features: {missing_features}")
                
                # Reorder columns to match training data
                input_df = input_df[self.feature_names]
                
                # Make prediction
                prediction = self.model.predict(input_df)[0]
                
                # Get prediction probability if available
                probability = None
                if hasattr(self.model, 'predict_proba'):
                    proba = self.model.predict_proba(input_df)[0]
                    probability = max(proba) if len(proba) > 0 else None
                
                return {
                    "prediction": prediction,
                    "confidence": probability,
                    "model_name": self.model_info.get("name"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
        
        @self.app.post("/predict-batch")
        async def predict_batch(input_data: List[Dict[str, Any]]):
            try:
                # Convert input to DataFrame
                input_df = pd.DataFrame(input_data)
                
                # Ensure all required features are present
                missing_features = set(self.feature_names) - set(input_df.columns)
                if missing_features:
                    raise HTTPException(status_code=400, detail=f"Missing features: {missing_features}")
                
                # Reorder columns to match training data
                input_df = input_df[self.feature_names]
                
                # Make predictions
                predictions = self.model.predict(input_df).tolist()
                
                # Get prediction probabilities if available
                probabilities = None
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba(input_df).max(axis=1).tolist()
                
                return {
                    "predictions": predictions,
                    "confidences": probabilities,
                    "model_name": self.model_info.get("name"),
                    "count": len(predictions),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8001):
        """Run the API server"""
        uvicorn.run(self.app, host=host, port=port)

class DeploymentManager:
    """Manages model deployment and API generation"""
    
    def __init__(self):
        self.deployment_configs = {}
        self.active_deployments = {}
    
    async def create_deployment(self, model_info: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create deployment for the trained model"""
        try:
            # Extract model details
            model_path = model_info.get("model_path")
            model_name = model_info.get("name")
            task_type = model_info.get("task_type")
            feature_names = model_info.get("data_info", {}).get("feature_names", [])
            
            if not model_path or not os.path.exists(model_path):
                raise ValueError("Model file not found")
            
            # Generate deployment configuration
            deployment_config = {
                "model_name": model_name,
                "task_type": task_type,
                "model_path": model_path,
                "feature_names": feature_names,
                "created_at": datetime.now().isoformat(),
                "deployment_id": f"deployment_{int(datetime.now().timestamp())}",
                "model_metrics": model_info.get("metrics", {}),
                "model_description": model_info.get("description", "")
            }
            
            # Generate API code
            api_code = self._generate_api_code(deployment_config)
            
            # Generate deployment scripts
            deployment_scripts = self._generate_deployment_scripts(deployment_config)
            
            # Generate Docker configuration
            docker_config = self._generate_docker_config(deployment_config)
            
            # Save deployment configuration
            deployment_dir = f"deployments/{deployment_config['deployment_id']}"
            os.makedirs(deployment_dir, exist_ok=True)
            
            # Save configuration
            with open(f"{deployment_dir}/config.json", 'w') as f:
                json.dump(deployment_config, f, indent=2)
            
            # Save API code
            with open(f"{deployment_dir}/api.py", 'w') as f:
                f.write(api_code)
            
            # Save deployment scripts
            for script_name, script_content in deployment_scripts.items():
                with open(f"{deployment_dir}/{script_name}", 'w') as f:
                    f.write(script_content)
            
            # Save Docker configuration
            with open(f"{deployment_dir}/Dockerfile", 'w') as f:
                f.write(docker_config['dockerfile'])
            
            with open(f"{deployment_dir}/requirements.txt", 'w') as f:
                f.write(docker_config['requirements'])
            
            # Generate usage example
            usage_example = self._generate_usage_example(deployment_config)
            with open(f"{deployment_dir}/usage_example.py", 'w') as f:
                f.write(usage_example)
            
            return {
                "deployment_id": deployment_config['deployment_id'],
                "deployment_path": deployment_dir,
                "api_endpoint": f"http://localhost:8001",
                "deployment_config": deployment_config,
                "files_created": [
                    "config.json", "api.py", "deploy.sh", "Dockerfile", 
                    "requirements.txt", "usage_example.py"
                ],
                "usage_instructions": "Run 'python api.py' to start the API server"
            }
            
        except Exception as e:
            raise Exception(f"Deployment creation failed: {str(e)}")
    
    def _generate_api_code(self, config: Dict[str, Any]) -> str:
        """Generate FastAPI code for model deployment"""
        
        api_template = f'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import uvicorn

# Load model
model = joblib.load("{config['model_path']}")
feature_names = {config['feature_names']}

app = FastAPI(
    title="AI Model API - {config['model_name']}",
    description="{config['model_description']}",
    version="1.0.0"
)

class PredictionRequest(BaseModel):
    """Request model for single prediction"""
'''
        
        # Add feature fields to request model
        for feature in config['feature_names']:
            api_template += f"    {feature}: Optional[Union[float, str, int]] = None\n"
        
        api_template += f'''
class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""
    data: List[Dict[str, Any]]

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: Union[str, float, int]
    confidence: Optional[float] = None
    model_name: str = "{config['model_name']}"
    timestamp: str

@app.get("/")
async def root():
    return {{
        "message": "AI Model API is running",
        "model_name": "{config['model_name']}",
        "task_type": "{config['task_type']}",
        "version": "1.0.0"
    }}

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "timestamp": datetime.now().isoformat()}}

@app.get("/model-info")
async def get_model_info():
    return {{
        "model_name": "{config['model_name']}",
        "task_type": "{config['task_type']}",
        "feature_names": feature_names,
        "model_metrics": {config.get('model_metrics', {})},
        "created_at": "{config['created_at']}"
    }}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: Dict[str, Any]):
    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([request])
        
        # Validate input
        missing_features = set(feature_names) - set(input_df.columns)
        if missing_features:
            raise HTTPException(status_code=400, detail=f"Missing features: {{missing_features}}")
        
        # Reorder columns
        input_df = input_df[feature_names]
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        
        # Get confidence if available
        confidence = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(input_df)[0]
            confidence = float(max(proba))
        
        return PredictionResponse(
            prediction=prediction,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {{str(e)}}")

@app.post("/predict-batch")
async def predict_batch(request: BatchPredictionRequest):
    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame(request.data)
        
        # Validate input
        missing_features = set(feature_names) - set(input_df.columns)
        if missing_features:
            raise HTTPException(status_code=400, detail=f"Missing features: {{missing_features}}")
        
        # Reorder columns
        input_df = input_df[feature_names]
        
        # Make predictions
        predictions = model.predict(input_df).tolist()
        
        # Get confidences if available
        confidences = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(input_df)
            confidences = [float(max(p)) for p in proba]
        
        return {{
            "predictions": predictions,
            "confidences": confidences,
            "count": len(predictions),
            "model_name": "{config['model_name']}",
            "timestamp": datetime.now().isoformat()
        }}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {{str(e)}}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''
        
        return api_template
    
    def _generate_deployment_scripts(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate deployment scripts"""
        
        # Shell script for deployment
        deploy_script = f'''#!/bin/bash

echo "Starting deployment for {config['model_name']}..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
echo "Starting API server..."
python api.py

# Or use gunicorn for production
echo "For production deployment, use:"
echo "gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8001"
'''
        
        # Docker deployment script
        docker_deploy = f'''#!/bin/bash

echo "Building Docker image for {config['model_name']}..."

docker build -t ai-model-{config['deployment_id']} .

echo "Running Docker container..."
docker run -p 8001:8001 ai-model-{config['deployment_id']}
'''
        
        return {
            "deploy.sh": deploy_script,
            "docker-deploy.sh": docker_deploy
        }
    
    def _generate_docker_config(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate Docker configuration"""
        
        dockerfile = f'''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "api.py"]
'''
        
        requirements = f'''fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2
joblib==1.3.2
pydantic==2.5.0
'''
        
        return {
            "dockerfile": dockerfile,
            "requirements": requirements
        }
    
    def _generate_usage_example(self, config: Dict[str, Any]) -> str:
        """Generate usage example code"""
        
        example_code = f'''import requests
import json

# API endpoint
API_URL = "http://localhost:8001"

def make_prediction(features):
    """Make a single prediction"""
    response = requests.post(f"{{API_URL}}/predict", json=features)
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction: {{result['prediction']}}")
        if result.get('confidence'):
            print(f"Confidence: {{result['confidence']:.4f}}")
        return result
    else:
        print(f"Error: {{response.status_code}} - {{response.text}}")
        return None

def make_batch_predictions(data_list):
    """Make batch predictions"""
    response = requests.post(f"{{API_URL}}/predict-batch", json={{"data": data_list}})
    if response.status_code == 200:
        result = response.json()
        print(f"Batch predictions: {{result['predictions']}}")
        print(f"Count: {{result['count']}}")
        return result
    else:
        print(f"Error: {{response.status_code}} - {{response.text}}")
        return None

# Example usage
if __name__ == "__main__":
    # Single prediction example
    sample_features = {{
'''
        
        # Add example feature values
        for feature in config['feature_names'][:3]:  # Use first 3 features as example
            example_code += f'        "{feature}": 1.0,\n'
        
        example_code += f'''    }}
    
    print("Making single prediction...")
    make_prediction(sample_features)
    
    # Batch prediction example
    batch_data = [
        {{"{config['feature_names'][0]}": 1.0, "{config['feature_names'][1]}": 2.0}},
        {{"{config['feature_names'][0]}": 3.0, "{config['feature_names'][1]}": 4.0}}
    ]
    
    print("\\nMaking batch predictions...")
    make_batch_predictions(batch_data)
    
    # Get model info
    print("\\nGetting model info...")
    response = requests.get(f"{{API_URL}}/model-info")
    if response.status_code == 200:
        model_info = response.json()
        print(f"Model: {{model_info['model_name']}}")
        print(f"Task Type: {{model_info['task_type']}}")
        print(f"Features: {{model_info['feature_names']}}")
'''
        
        return example_code