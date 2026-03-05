# Jupyter Notebooks for AI Data Engineer Agent

This directory contains example notebooks demonstrating the AI Data Engineer Agent capabilities.

## Available Notebooks

### 1. Dataset Analysis Demo
- **File**: `01_dataset_analysis_demo.ipynb`
- **Description**: Demonstrates automated dataset profiling and analysis
- **Features**: Quality assessment, column type detection, missing value analysis

### 2. Pipeline Generation Demo
- **File**: `02_pipeline_generation_demo.ipynb`
- **Description**: Shows automatic ML pipeline creation
- **Features**: Data cleaning, feature engineering, model selection

### 3. Model Training Demo
- **File**: `03_model_training_demo.ipynb`
- **Description**: Demonstrates automated model training and comparison
- **Features**: Multiple model training, cross-validation, performance metrics

### 4. API Deployment Demo
- **File**: `04_api_deployment_demo.ipynb`
- **Description**: Shows model deployment and API generation
- **Features**: FastAPI integration, endpoint testing, monitoring

### 5. Complete Workflow Demo
- **File**: `05_complete_workflow_demo.ipynb`
- **Description**: End-to-end demonstration of the entire system
- **Features**: Full pipeline from dataset to deployed API

## Running the Notebooks

### Local Setup
```bash
# Install Jupyter and dependencies
pip install jupyter jupyterlab pandas numpy matplotlib seaborn scikit-learn

# Start Jupyter Lab
jupyter lab
```

### Docker Setup
```bash
# Run Jupyter container
docker-compose up jupyter

# Access Jupyter at http://localhost:8888
```

## Notebook Structure

Each notebook follows this pattern:
1. **Data Loading**: Load sample datasets
2. **Analysis**: Demonstrate AI-powered analysis
3. **Pipeline Creation**: Show automated pipeline generation
4. **Model Training**: Train and compare multiple models
5. **Results**: Display performance metrics and insights
6. **Deployment**: Generate API endpoints

## Customization

You can modify the notebooks to:
- Test with your own datasets
- Experiment with different parameters
- Add new analysis techniques
- Create custom visualizations