import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
import ast
import re

class PipelineGenerator:
    """AI-powered pipeline generation for data processing and ML"""
    
    def __init__(self):
        # Initialize LangChain with OpenAI (you can use other models too)
        self.llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo-instruct")
        
    async def generate_pipeline(self, analysis_results: Dict[str, Any], target_column: str, task_type: str) -> Dict[str, Any]:
        """Generate complete ML pipeline based on dataset analysis"""
        try:
            # Generate data cleaning steps
            cleaning_steps = await self._generate_cleaning_steps(analysis_results)
            
            # Generate feature engineering steps
            feature_steps = await self._generate_feature_engineering(analysis_results, target_column)
            
            # Generate model selection and training code
            model_code = await self._generate_model_code(analysis_results, target_column, task_type)
            
            # Generate evaluation and validation code
            evaluation_code = await self._generate_evaluation_code(task_type)
            
            # Combine into complete pipeline
            pipeline = {
                "cleaning_steps": cleaning_steps,
                "feature_engineering": feature_steps,
                "model_training": model_code,
                "evaluation": evaluation_code,
                "task_type": task_type,
                "target_column": target_column,
                "generated_code": self._combine_pipeline_code(cleaning_steps, feature_steps, model_code, evaluation_code)
            }
            
            return pipeline
            
        except Exception as e:
            raise Exception(f"Pipeline generation failed: {str(e)}")
    
    async def _generate_cleaning_steps(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate data cleaning steps based on quality assessment"""
        quality = analysis_results.get("quality", {})
        columns = analysis_results.get("columns", {})
        
        cleaning_steps = []
        
        # Handle missing values
        missing_info = quality.get("missing_values", {})
        if missing_info.get("total_missing", 0) > 0:
            columns_with_missing = missing_info.get("columns_with_missing", {})
            
            for col, missing_count in columns_with_missing.items():
                if col in columns:
                    col_type = columns[col].get("type", "unknown")
                    missing_pct = columns[col].get("null_percentage", 0)
                    
                    if missing_pct > 50:
                        cleaning_steps.append({
                            "step": "drop_column",
                            "column": col,
                            "reason": f"High missing percentage: {missing_pct:.1f}%"
                        })
                    elif col_type == "numerical":
                        cleaning_steps.append({
                            "step": "impute_numerical",
                            "column": col,
                            "method": "median",
                            "reason": f"Numerical column with {missing_pct:.1f}% missing values"
                        })
                    elif col_type == "categorical":
                        cleaning_steps.append({
                            "step": "impute_categorical",
                            "column": col,
                            "method": "mode",
                            "reason": f"Categorical column with {missing_pct:.1f}% missing values"
                        })
        
        # Handle duplicates
        duplicates = quality.get("duplicates", {})
        if duplicates.get("duplicate_rows", 0) > 0:
            cleaning_steps.append({
                "step": "remove_duplicates",
                "reason": f"Found {duplicates['duplicate_rows']} duplicate rows"
            })
        
        # Handle outliers for numerical columns
        for col, col_info in columns.items():
            if col_info.get("type") == "numerical":
                outlier_pct = col_info.get("outlier_percentage", 0)
                if outlier_pct > 5:
                    cleaning_steps.append({
                        "step": "handle_outliers",
                        "column": col,
                        "method": "winsorization",
                        "reason": f"High outlier percentage: {outlier_pct:.1f}%"
                    })
        
        return cleaning_steps
    
    async def _generate_feature_engineering(self, analysis_results: Dict[str, Any], target_column: str) -> List[Dict[str, Any]]:
        """Generate feature engineering steps"""
        columns = analysis_results.get("columns", {})
        correlations = analysis_results.get("correlations", {})
        
        feature_steps = []
        
        # One-hot encoding for categorical variables
        categorical_cols = [col for col, info in columns.items() 
                          if info.get("type") == "categorical" and col != target_column]
        
        if categorical_cols:
            feature_steps.append({
                "step": "one_hot_encode",
                "columns": categorical_cols,
                "reason": f"Encoding {len(categorical_cols)} categorical variables"
            })
        
        # Scaling for numerical variables
        numerical_cols = [col for col, info in columns.items() 
                         if info.get("type") == "numerical" and col != target_column]
        
        if numerical_cols:
            feature_steps.append({
                "step": "scale_features",
                "columns": numerical_cols,
                "method": "standard_scaler",
                "reason": f"Scaling {len(numerical_cols)} numerical features"
            })
        
        # Feature interactions for highly correlated variables
        high_correlations = correlations.get("high_correlations", [])
        if high_correlations:
            for corr in high_correlations[:3]:  # Limit to top 3
                col1, col2 = corr["column1"], corr["column2"]
                if col1 != target_column and col2 != target_column:
                    feature_steps.append({
                        "step": "create_interaction_feature",
                        "columns": [col1, col2],
                        "method": "multiply",
                        "reason": f"High correlation ({corr['correlation']:.2f}) suggests interaction"
                    })
        
        # Polynomial features for numerical columns
        if len(numerical_cols) > 0:
            feature_steps.append({
                "step": "polynomial_features",
                "columns": numerical_cols[:3],  # Top 3 numerical columns
                "degree": 2,
                "reason": "Adding polynomial features for non-linear relationships"
            })
        
        return feature_steps
    
    async def _generate_model_code(self, analysis_results: Dict[str, Any], target_column: str, task_type: str) -> Dict[str, Any]:
        """Generate model training code"""
        
        # Model selection based on task type and data characteristics
        if task_type == "classification":
            models = [
                {
                    "name": "RandomForestClassifier",
                    "params": {"n_estimators": 100, "random_state": 42},
                    "reason": "Good baseline for classification with feature importance"
                },
                {
                    "name": "XGBClassifier",
                    "params": {"n_estimators": 100, "random_state": 42},
                    "reason": "State-of-the-art gradient boosting"
                },
                {
                    "name": "LogisticRegression",
                    "params": {"random_state": 42, "max_iter": 1000},
                    "reason": "Linear baseline and interpretable"
                }
            ]
        else:  # regression
            models = [
                {
                    "name": "RandomForestRegressor",
                    "params": {"n_estimators": 100, "random_state": 42},
                    "reason": "Robust to outliers and non-linear relationships"
                },
                {
                    "name": "XGBRegressor",
                    "params": {"n_estimators": 100, "random_state": 42},
                    "reason": "High performance for regression tasks"
                },
                {
                    "name": "LinearRegression",
                    "params": {},
                    "reason": "Simple baseline for linear relationships"
                }
            ]
        
        # Generate training code template
        training_code = self._generate_training_template(task_type, target_column, models)
        
        return {
            "models": models,
            "training_code": training_code,
            "cross_validation": {
                "method": "StratifiedKFold" if task_type == "classification" else "KFold",
                "n_splits": 5,
                "scoring": "accuracy" if task_type == "classification" else "r2"
            }
        }
    
    async def _generate_evaluation_code(self, task_type: str) -> Dict[str, Any]:
        """Generate model evaluation code"""
        if task_type == "classification":
            metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
            plots = ["confusion_matrix", "roc_curve", "classification_report"]
        else:
            metrics = ["mse", "rmse", "mae", "r2", "mape"]
            plots = ["residual_plot", "prediction_vs_actual", "feature_importance"]
        
        return {
            "metrics": metrics,
            "plots": plots,
            "validation_method": "train_test_split",
            "test_size": 0.2,
            "random_state": 42
        }
    
    def _generate_training_template(self, task_type: str, target_column: str, models: List[Dict]) -> str:
        """Generate Python training code template"""
        
        code_template = f'''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import {'accuracy_score, classification_report, confusion_matrix' if task_type == 'classification' else 'mean_squared_error, r2_score, mean_absolute_error'}
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns

class ModelTrainer:
    def __init__(self):
        self.models = {{}}
        self.results = {{}}
        self.best_model = None
        self.scaler = StandardScaler()
        
    def preprocess_data(self, X, y):
        """Preprocess data based on generated pipeline"""
        # Handle missing values
        X = X.fillna(X.median())
        
        # Scale numerical features
        numerical_cols = X.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            X[numerical_cols] = self.scaler.fit_transform(X[numerical_cols])
        
        return X, y
    
    def train_models(self, X, y):
        """Train multiple models and select the best one"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Define models
        models = {{
'''
        
        # Add model definitions
        for i, model in enumerate(models):
            code_template += f'''            "{model['name']}": {model['name']}(**{model['params']}),
'''
        
        code_template += f'''        }}
        
        # Train and evaluate each model
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                self.models[name] = model
                
                # Predictions
                y_pred = model.predict(X_test)
                
                # Evaluation
'''
        
        if task_type == "classification":
            code_template += f'''
                accuracy = accuracy_score(y_test, y_pred)
                self.results[name] = {{'accuracy': accuracy, 'model': model}}
                print(f"{{name}}: Accuracy = {{accuracy:.4f}}")
'''
        else:
            code_template += f'''
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)
                self.results[name] = {{'mse': mse, 'rmse': rmse, 'r2': r2, 'model': model}}
                print(f"{{name}}: RMSE = {{rmse:.4f}}, R² = {{r2:.4f}}")
'''
        
        code_template += f'''
            except Exception as e:
                print(f"Error training {{name}}: {{str(e)}}")
        
        # Select best model
        if self.results:
            if task_type == 'classification':
                self.best_model = max(self.results.items(), key=lambda x: x[1]['accuracy'])[1]['model']
            else:
                self.best_model = max(self.results.items(), key=lambda x: x[1]['r2'])[1]['model']
        
        return self.best_model
    
    def get_feature_importance(self, model_name):
        """Get feature importance for tree-based models"""
        if model_name in self.models:
            model = self.models[model_name]
            if hasattr(model, 'feature_importances_'):
                return model.feature_importances_
        return None

# Usage example:
# trainer = ModelTrainer()
# X_processed, y_processed = trainer.preprocess_data(X, y)
# best_model = trainer.train_models(X_processed, y_processed)
'''
        
        return code_template
    
    def _combine_pipeline_code(self, cleaning_steps: List[Dict], feature_steps: List[Dict], 
                             model_code: Dict, evaluation_code: Dict) -> str:
        """Combine all pipeline components into executable code"""
        
        combined_code = '''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns

class AutoPipeline:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.imputers = {}
        self.trained_models = {}
        
    def clean_data(self, df):
        """Apply generated cleaning steps"""
        df_clean = df.copy()
        
        # Remove duplicates
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        print(f"Removed {initial_rows - len(df_clean)} duplicate rows")
        
        # Handle missing values
        for col in df_clean.columns:
            if df_clean[col].isnull().sum() > 0:
                if df_clean[col].dtype in ['int64', 'float64']:
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                else:
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
        
        return df_clean
    
    def engineer_features(self, X, y=None):
        """Apply generated feature engineering"""
        X_engineered = X.copy()
        
        # One-hot encode categorical variables
        categorical_cols = X_engineered.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            X_engineered = pd.get_dummies(X_engineered, columns=categorical_cols, drop_first=True)
        
        # Scale numerical features
        numerical_cols = X_engineered.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            X_engineered[numerical_cols] = self.scaler.fit_transform(X_engineered[numerical_cols])
        
        return X_engineered
    
    def run_pipeline(self, df, target_column, task_type):
        """Run the complete pipeline"""
        print("Starting automated pipeline...")
        
        # Clean data
        df_clean = self.clean_data(df)
        print(f"Data cleaned: {len(df_clean)} rows, {len(df_clean.columns)} columns")
        
        # Separate features and target
        X = df_clean.drop(columns=[target_column])
        y = df_clean[target_column]
        
        # Feature engineering
        X_engineered = self.engineer_features(X, y)
        print(f"Features engineered: {X_engineered.shape[1]} features")
        
        return X_engineered, y

# Usage:
# pipeline = AutoPipeline()
# X_processed, y_processed = pipeline.run_pipeline(df, 'target_column', 'classification')
'''
        
        return combined_code