import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
import xgboost as xgb
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import shap
from datetime import datetime

class ModelBuilder:
    """Advanced model building with automatic selection and hyperparameter tuning"""
    
    def __init__(self):
        self.trained_models = {}
        self.best_model = None
        self.results = {}
        self.preprocessor = None
        
    async def train_model(self, file_path: str, target_column: str, task_type: str, pipeline_code: str = None) -> Dict[str, Any]:
        """Train multiple models and select the best one"""
        try:
            # Load and preprocess data
            X, y = await self._load_and_preprocess_data(file_path, target_column, pipeline_code)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if task_type == "classification" else None)
            
            # Define models based on task type
            models = self._get_model_candidates(task_type)
            
            # Train and evaluate models
            model_results = await self._train_and_evaluate_models(models, X_train, X_test, y_train, y_test, task_type)
            
            # Select best model
            best_model_info = self._select_best_model(model_results, task_type)
            
            # Generate feature importance and SHAP explanations
            explanations = await self._generate_explanations(best_model_info, X_test, task_type)
            
            # Save best model
            model_path = await self._save_model(best_model_info, file_path)
            
            return {
                "task_type": task_type,
                "target_column": target_column,
                "best_model": best_model_info,
                "all_models": model_results,
                "explanations": explanations,
                "model_path": model_path,
                "training_timestamp": datetime.now().isoformat(),
                "data_info": {
                    "n_samples": len(X),
                    "n_features": X.shape[1],
                    "feature_names": X.columns.tolist()
                }
            }
            
        except Exception as e:
            raise Exception(f"Model training failed: {str(e)}")
    
    async def _load_and_preprocess_data(self, file_path: str, target_column: str, pipeline_code: str = None) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and preprocess data"""
        # Load dataset
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Separate features and target
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset")
        
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Apply preprocessing pipeline
        X_processed = self._apply_preprocessing(X, y)
        
        return X_processed, y
    
    def _apply_preprocessing(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Apply preprocessing steps"""
        X_processed = X.copy()
        
        # Handle missing values
        for col in X_processed.columns:
            if X_processed[col].isnull().sum() > 0:
                if X_processed[col].dtype in ['int64', 'float64']:
                    X_processed[col].fillna(X_processed[col].median(), inplace=True)
                else:
                    X_processed[col].fillna(X_processed[col].mode()[0], inplace=True)
        
        # Encode categorical variables
        categorical_cols = X_processed.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            X_processed = pd.get_dummies(X_processed, columns=categorical_cols, drop_first=True)
        
        # Scale numerical features
        numerical_cols = X_processed.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            scaler = StandardScaler()
            X_processed[numerical_cols] = scaler.fit_transform(X_processed[numerical_cols])
            self.preprocessor = scaler
        
        return X_processed
    
    def _get_model_candidates(self, task_type: str) -> List[Dict[str, Any]]:
        """Get list of model candidates"""
        if task_type == "classification":
            return [
                {
                    "name": "RandomForestClassifier",
                    "model": RandomForestClassifier(n_estimators=100, random_state=42),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [3, 5, 7, None],
                        "min_samples_split": [2, 5, 10]
                    },
                    "description": "Ensemble method with feature importance"
                },
                {
                    "name": "XGBClassifier",
                    "model": xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss'),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [3, 5, 7],
                        "learning_rate": [0.01, 0.1, 0.3]
                    },
                    "description": "Gradient boosting with high performance"
                },
                {
                    "name": "LogisticRegression",
                    "model": LogisticRegression(random_state=42, max_iter=1000),
                    "params": {
                        "C": [0.1, 1, 10],
                        "penalty": ['l1', 'l2'],
                        "solver": ['liblinear']
                    },
                    "description": "Linear model with interpretability"
                }
            ]
        else:  # regression
            return [
                {
                    "name": "RandomForestRegressor",
                    "model": RandomForestRegressor(n_estimators=100, random_state=42),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [3, 5, 7, None],
                        "min_samples_split": [2, 5, 10]
                    },
                    "description": "Ensemble method for regression"
                },
                {
                    "name": "XGBRegressor",
                    "model": xgb.XGBRegressor(n_estimators=100, random_state=42),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [3, 5, 7],
                        "learning_rate": [0.01, 0.1, 0.3]
                    },
                    "description": "Gradient boosting for regression"
                },
                {
                    "name": "LinearRegression",
                    "model": LinearRegression(),
                    "params": {},
                    "description": "Simple linear baseline"
                }
            ]
    
    async def _train_and_evaluate_models(self, models: List[Dict], X_train: pd.DataFrame, X_test: pd.DataFrame, 
                                       y_train: pd.Series, y_test: pd.Series, task_type: str) -> Dict[str, Any]:
        """Train and evaluate all model candidates"""
        results = {}
        
        for model_info in models:
            try:
                model_name = model_info["name"]
                model = model_info["model"]
                params = model_info.get("params", {})
                
                print(f"Training {model_name}...")
                
                # Hyperparameter tuning if parameters provided
                if params:
                    grid_search = GridSearchCV(model, params, cv=3, scoring='accuracy' if task_type == 'classification' else 'r2', n_jobs=-1)
                    grid_search.fit(X_train, y_train)
                    best_model = grid_search.best_estimator_
                    best_params = grid_search.best_params_
                else:
                    model.fit(X_train, y_train)
                    best_model = model
                    best_params = {}
                
                # Make predictions
                y_pred = best_model.predict(X_test)
                
                # Calculate metrics
                if task_type == "classification":
                    metrics = {
                        "accuracy": accuracy_score(y_test, y_pred),
                        "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
                        "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
                        "f1": f1_score(y_test, y_pred, average='weighted', zero_division=0)
                    }
                else:
                    metrics = {
                        "mse": mean_squared_error(y_test, y_pred),
                        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                        "mae": mean_absolute_error(y_test, y_pred),
                        "r2": r2_score(y_test, y_pred)
                    }
                
                # Cross-validation scores
                cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, 
                                          scoring='accuracy' if task_type == 'classification' else 'r2')
                
                results[model_name] = {
                    "model": best_model,
                    "metrics": metrics,
                    "cv_mean": cv_scores.mean(),
                    "cv_std": cv_scores.std(),
                    "best_params": best_params,
                    "predictions": y_pred,
                    "description": model_info["description"]
                }
                
                print(f"{model_name} completed - CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
                
            except Exception as e:
                print(f"Error training {model_info['name']}: {str(e)}")
                continue
        
        return results
    
    def _select_best_model(self, model_results: Dict[str, Any], task_type: str) -> Dict[str, Any]:
        """Select the best model based on performance"""
        if not model_results:
            raise ValueError("No models were successfully trained")
        
        if task_type == "classification":
            # Select based on accuracy
            best_model_name = max(model_results.items(), key=lambda x: x[1]['metrics']['accuracy'])[0]
        else:
            # Select based on R² score
            best_model_name = max(model_results.items(), key=lambda x: x[1]['metrics']['r2'])[0]
        
        return {
            "name": best_model_name,
            "model": model_results[best_model_name]['model'],
            "metrics": model_results[best_model_name]['metrics'],
            "cv_score": model_results[best_model_name]['cv_mean'],
            "description": model_results[best_model_name]['description']
        }
    
    async def _generate_explanations(self, best_model_info: Dict[str, Any], X_test: pd.DataFrame, task_type: str) -> Dict[str, Any]:
        """Generate model explanations using SHAP"""
        explanations = {}
        
        try:
            model = best_model_info['model']
            model_name = best_model_info['name']
            
            # Feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                feature_importance = model.feature_importances_
                feature_names = X_test.columns
                
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': feature_importance
                }).sort_values('importance', ascending=False)
                
                explanations['feature_importance'] = importance_df.to_dict('records')
            
            # SHAP explanations
            if model_name in ['XGBClassifier', 'XGBRegressor', 'RandomForestClassifier', 'RandomForestRegressor']:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_test[:100])  # Limit for performance
                
                explanations['shap_summary'] = {
                    'mean_abs_shap': np.mean(np.abs(shap_values), axis=0).tolist() if len(shap_values.shape) > 1 else np.mean(np.abs(shap_values)).tolist(),
                    'feature_names': X_test.columns.tolist()
                }
            
        except Exception as e:
            print(f"SHAP explanation failed: {str(e)}")
            explanations['shap_error'] = str(e)
        
        return explanations
    
    async def _save_model(self, best_model_info: Dict[str, Any], original_file_path: str) -> str:
        """Save the best trained model"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"best_model_{best_model_info['name']}_{timestamp}.pkl"
        model_path = f"models/{model_filename}"
        
        # Create models directory if it doesn't exist
        import os
        os.makedirs('models', exist_ok=True)
        
        # Save model
        joblib.dump(best_model_info['model'], model_path)
        
        return model_path