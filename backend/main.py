from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

app = FastAPI(
    title="AI Data Engineer Agent",
    description="Autonomous AI system for data analysis and ML pipeline generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "datasets"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

class DataEngineerAgent:
    def __init__(self):
        from api.dataset_analyzer import DatasetAnalyzer
        from api.pipeline_generator import PipelineGenerator
        from api.model_builder import ModelBuilder
        from api.deployment_manager import DeploymentManager
        self.analyzer = DatasetAnalyzer()
        self.pipeline_generator = PipelineGenerator()
        self.model_builder = ModelBuilder()
        self.deployment_manager = DeploymentManager()
        
    async def process_dataset(self, file_path: str, target_column: str, task_type: str) -> Dict[str, Any]:
        try:
            analysis_results = await self.analyzer.analyze_dataset(file_path)
            pipeline_code = await self.pipeline_generator.generate_pipeline(
                analysis_results, target_column, task_type
            )
            model_results = await self.model_builder.train_model(
                file_path, target_column, task_type, pipeline_code
            )
            deployment_info = await self.deployment_manager.create_deployment(
                model_results['model'], analysis_results
            )
            return {
                "analysis": analysis_results,
                "pipeline": pipeline_code,
                "model": model_results,
                "deployment": deployment_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

_agent = None

def get_agent() -> DataEngineerAgent:
    global _agent
    if _agent is None:
        try:
            _agent = DataEngineerAgent()
        except ImportError as e:
            raise HTTPException(status_code=503, detail=f"Dependency not available: {str(e)}")
    return _agent

@app.post("/api/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx', '.json')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return JSONResponse({
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "message": "File uploaded successfully"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/api/analyze-dataset/{file_id}")
async def analyze_dataset(file_id: str, background_tasks: BackgroundTasks, target_column: str = None, task_type: str = "classification"):
    file_path = None
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(f"{file_id}_"):
            file_path = os.path.join(UPLOAD_DIR, filename)
            break
    if not file_path:
        raise HTTPException(status_code=404, detail="Dataset not found")
    task_id = str(uuid.uuid4())
    async def process_task():
        try:
            results = await get_agent().process_dataset(file_path, target_column, task_type)
            result_path = os.path.join(RESULTS_DIR, f"{task_id}.json")
            with open(result_path, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            error_result = {"error": str(e), "timestamp": datetime.now().isoformat()}
            result_path = os.path.join(RESULTS_DIR, f"{task_id}.json")
            with open(result_path, 'w') as f:
                json.dump(error_result, f, indent=2)
    background_tasks.add_task(process_task)
    return JSONResponse({
        "task_id": task_id,
        "message": "Dataset analysis started in background"
    })

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    result_path = os.path.join(RESULTS_DIR, f"{task_id}.json")
    if os.path.exists(result_path):
        with open(result_path, 'r') as f:
            result = json.load(f)
        return JSONResponse({
            "status": "completed",
            "result": result
        })
    else:
        return JSONResponse({
            "status": "processing",
            "message": "Task is still being processed"
        })

@app.get("/api/datasets")
async def list_datasets():
    datasets = []
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith(('.csv', '.xlsx', '.json')):
            file_path = os.path.join(UPLOAD_DIR, filename)
            stat = os.stat(file_path)
            datasets.append({
                "filename": filename,
                "size": stat.st_size,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    return datasets

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
