import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import ydata_profiling as pp
from datetime import datetime
import json

class DatasetAnalyzer:
    """Advanced dataset analysis with AI-powered insights"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    async def analyze_dataset(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive dataset analysis"""
        try:
            # Load dataset
            df = await self._load_dataset(file_path)
            
            # Basic statistics
            basic_stats = self._get_basic_stats(df)
            
            # Data quality assessment
            quality_assessment = self._assess_data_quality(df)
            
            # Column analysis
            column_analysis = self._analyze_columns(df)
            
            # Correlation analysis
            correlation_analysis = self._analyze_correlations(df)
            
            # Target variable suggestions
            target_suggestions = self._suggest_target_variables(df, column_analysis)
            
            # Generate profiling report
            profiling_report = self._generate_profiling_report(df)
            
            return {
                "basic_stats": basic_stats,
                "quality": quality_assessment,
                "columns": column_analysis,
                "correlations": correlation_analysis,
                "target_suggestions": target_suggestions,
                "profiling_report": profiling_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Dataset analysis failed: {str(e)}")
    
    async def _load_dataset(self, file_path: str) -> pd.DataFrame:
        """Load dataset from various formats"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format")
    
    def _get_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic dataset statistics"""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "dtypes": df.dtypes.value_counts().to_dict()
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality issues"""
        missing_values = df.isnull().sum()
        duplicate_rows = df.duplicated().sum()
        
        return {
            "missing_values": {
                "total_missing": missing_values.sum(),
                "columns_with_missing": missing_values[missing_values > 0].to_dict(),
                "missing_percentage": (missing_values.sum() / (len(df) * len(df.columns))) * 100
            },
            "duplicates": {
                "duplicate_rows": duplicate_rows,
                "duplicate_percentage": (duplicate_rows / len(df)) * 100
            },
            "data_quality_score": self._calculate_quality_score(df)
        }
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score"""
        missing_penalty = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 0.3
        duplicate_penalty = (df.duplicated().sum() / len(df)) * 0.2
        
        # Check for constant columns
        constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
        constant_penalty = len(constant_cols) / len(df.columns) * 0.2
        
        quality_score = max(0.0, 1.0 - missing_penalty - duplicate_penalty - constant_penalty)
        return round(quality_score, 3)
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze each column in detail"""
        column_info = {}
        
        for col in df.columns:
            col_data = df[col]
            
            analysis = {
                "dtype": str(col_data.dtype),
                "unique_values": col_data.nunique(),
                "null_count": col_data.isnull().sum(),
                "null_percentage": (col_data.isnull().sum() / len(df)) * 100,
            }
            
            # Categorical analysis
            if col_data.dtype == 'object' or col_data.nunique() < len(df) * 0.1:
                analysis["type"] = "categorical"
                analysis["value_counts"] = col_data.value_counts().head(10).to_dict()
                analysis["cardinality"] = col_data.nunique()
            
            # Numerical analysis
            elif pd.api.types.is_numeric_dtype(col_data):
                analysis["type"] = "numerical"
                analysis["statistics"] = {
                    "mean": col_data.mean(),
                    "median": col_data.median(),
                    "std": col_data.std(),
                    "min": col_data.min(),
                    "max": col_data.max(),
                    "skewness": col_data.skew(),
                    "kurtosis": col_data.kurtosis()
                }
                
                # Check for outliers
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                outliers = col_data[(col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)]
                analysis["outliers"] = len(outliers)
                analysis["outlier_percentage"] = (len(outliers) / len(df)) * 100
            
            # Date analysis
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                analysis["type"] = "datetime"
                analysis["date_range"] = {
                    "start": col_data.min().isoformat(),
                    "end": col_data.max().isoformat()
                }
            
            column_info[col] = analysis
        
        return column_info
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numerical columns"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {"message": "Insufficient numerical columns for correlation analysis"}
        
        correlation_matrix = df[numerical_cols].corr()
        
        # Find high correlations
        high_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # High correlation threshold
                    high_correlations.append({
                        "column1": correlation_matrix.columns[i],
                        "column2": correlation_matrix.columns[j],
                        "correlation": corr_value
                    })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "high_correlations": high_correlations,
            "correlation_insights": f"Found {len(high_correlations)} high correlations (|r| > 0.7)"
        }
    
    def _suggest_target_variables(self, df: pd.DataFrame, column_analysis: Dict) -> List[Dict[str, Any]]:
        """Suggest potential target variables based on analysis"""
        suggestions = []
        
        for col, analysis in column_analysis.items():
            score = 0
            reasons = []
            
            # Binary classification target
            if analysis.get("type") == "categorical" and analysis.get("unique_values") == 2:
                score += 3
                reasons.append("Binary categorical variable")
            
            # Multi-class classification target
            elif analysis.get("type") == "categorical" and 2 < analysis.get("unique_values", 0) <= 20:
                score += 2
                reasons.append("Multi-class categorical variable")
            
            # Regression target
            elif analysis.get("type") == "numerical":
                score += 2
                reasons.append("Numerical variable suitable for regression")
                
                # Check for normal distribution
                if abs(analysis.get("statistics", {}).get("skewness", 0)) < 2:
                    score += 1
                    reasons.append("Relatively normal distribution")
            
            # Check if column name suggests target
            target_keywords = ['target', 'label', 'class', 'category', 'outcome', 'result', 'prediction']
            if any(keyword in col.lower() for keyword in target_keywords):
                score += 2
                reasons.append("Column name suggests target variable")
            
            if score > 0:
                suggestions.append({
                    "column": col,
                    "score": score,
                    "reasons": reasons,
                    "type": "classification" if analysis.get("type") == "categorical" else "regression"
                })
        
        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:5]  # Top 5 suggestions
    
    def _generate_profiling_report(self, df: pd.DataFrame) -> str:
        """Generate ydata-profiling report"""
        try:
            profile = pp.ProfileReport(df, title="Dataset Profile Report", explorative=True)
            report_path = f"results/profile_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            profile.to_file(report_path)
            return report_path
        except Exception as e:
            return f"Profiling report generation failed: {str(e)}"