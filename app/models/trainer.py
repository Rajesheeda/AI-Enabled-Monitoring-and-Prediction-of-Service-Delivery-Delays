"""
Model Training Module
Trains delay prediction models on historical data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import os
from pathlib import Path

try:
    import xgboost as xgb
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, r2_score
except ImportError:
    xgb = None
    RandomForestClassifier = None
    RandomForestRegressor = None

from .predictor import DelayPredictor

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trains delay prediction models"""
    
    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self.predictor = DelayPredictor()
        self.label_encoders = {}
        
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data from DataFrame"""
        try:
            # Create target variables
            df['is_delayed'] = (df['actual_completion'] > df['expected_completion']).astype(int)
            df['delay_hours'] = (df['actual_completion'] - df['expected_completion']).dt.total_seconds() / 3600
            df['delay_hours'] = df['delay_hours'].clip(lower=0)  # Only positive delays
            
            # Calculate days since submission
            df['days_since_submission'] = (df['actual_completion'] - df['submitted_at']).dt.total_seconds() / 86400
            
            # Encode categorical features
            categorical_cols = ['current_stage', 'district', 'mandal', 'service_code', 'category']
            for col in categorical_cols:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
            
            # Calculate historical delay rates (simplified - would need actual historical data)
            df['historical_delay_rate_district'] = df.groupby('district')['is_delayed'].transform('mean')
            df['historical_delay_rate_mandal'] = df.groupby('mandal')['is_delayed'].transform('mean')
            df['historical_delay_rate_service'] = df.groupby('service_code')['is_delayed'].transform('mean')
            
            # Workload features (placeholder - would need actual workload data)
            df['workload_at_stage'] = df.groupby(['current_stage', 'district']).transform('size') / 100
            
            # Time features
            df['day_of_week'] = df['submitted_at'].dt.dayofweek
            df['month'] = df['submitted_at'].dt.month
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # Select features
            feature_columns = [
                'days_since_submission', 'current_stage_encoded', 'district_encoded',
                'mandal_encoded', 'service_code_encoded', 'category_encoded',
                'workload_at_stage', 'historical_delay_rate_district',
                'historical_delay_rate_mandal', 'historical_delay_rate_service',
                'day_of_week', 'month', 'is_weekend'
            ]
            
            X = df[feature_columns].fillna(0).values
            y_classifier = df['is_delayed'].values
            y_regressor = df['delay_hours'].values
            
            return X, y_classifier, y_regressor
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """Train delay prediction models"""
        try:
            logger.info("Preparing training data...")
            X, y_classifier, y_regressor = self.prepare_training_data(df)
            
            # Split data
            X_train, X_test, y_train_clf, y_test_clf, y_train_reg, y_test_reg = train_test_split(
                X, y_classifier, y_regressor, test_size=test_size, random_state=42
            )
            
            logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")
            
            # Train classifier
            logger.info("Training delay classifier...")
            if self.model_type == "xgboost" and xgb:
                classifier = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    eval_metric='logloss'
                )
            else:
                classifier = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            
            classifier.fit(X_train, y_train_clf)
            self.predictor.delay_classifier = classifier
            
            # Train regressor
            logger.info("Training delay regressor...")
            if self.model_type == "xgboost" and xgb:
                regressor = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            else:
                regressor = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            
            regressor.fit(X_train, y_train_reg)
            self.predictor.delay_regressor = regressor
            
            # Update label encoders
            self.predictor.label_encoders = self.label_encoders
            
            # Evaluate models
            logger.info("Evaluating models...")
            metrics = self._evaluate_models(X_test, y_test_clf, y_test_reg)
            
            # Save models
            self.predictor.save_models()
            
            logger.info("Training completed successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    def _evaluate_models(self, X_test: np.ndarray, y_test_clf: np.ndarray, y_test_reg: np.ndarray) -> Dict:
        """Evaluate model performance"""
        try:
            # Classifier metrics
            y_pred_clf = self.predictor.delay_classifier.predict(X_test)
            y_pred_proba = self.predictor.delay_classifier.predict_proba(X_test)[:, 1]
            
            clf_accuracy = accuracy_score(y_test_clf, y_pred_clf)
            clf_precision = precision_score(y_test_clf, y_pred_clf, zero_division=0)
            clf_recall = recall_score(y_test_clf, y_pred_clf, zero_division=0)
            clf_f1 = f1_score(y_test_clf, y_pred_clf, zero_division=0)
            
            # Regressor metrics
            y_pred_reg = self.predictor.delay_regressor.predict(X_test)
            reg_mae = mean_absolute_error(y_test_reg, y_pred_reg)
            reg_r2 = r2_score(y_test_reg, y_pred_reg)
            
            metrics = {
                'classifier': {
                    'accuracy': float(clf_accuracy),
                    'precision': float(clf_precision),
                    'recall': float(clf_recall),
                    'f1_score': float(clf_f1)
                },
                'regressor': {
                    'mean_absolute_error': float(reg_mae),
                    'r2_score': float(reg_r2)
                },
                'overall_accuracy': float(clf_accuracy)  # For PoC success criteria
            }
            
            logger.info(f"Model Metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating models: {e}")
            return {}
    
    def generate_sample_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate sample training data for demonstration"""
        np.random.seed(42)
        
        districts = ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Anantapur']
        mandals = ['Urban', 'Rural', 'Semi-Urban']
        services = [f'CAT-B-{i:03d}' for i in range(1, 51)]
        stages = ['APPLICATION', 'VRO', 'REVENUE_INSPECTOR', 'TAHSILDAR', 'FINAL_PROCESSING', 'DELIVERED']
        categories = ['CATEGORY_A', 'CATEGORY_B', 'CATEGORY_C']
        
        data = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(n_samples):
            submitted_at = base_date + timedelta(days=np.random.randint(0, 365))
            sla_days = np.random.choice([3, 7, 15], p=[0.1, 0.7, 0.2])
            expected_completion = submitted_at + timedelta(days=sla_days)
            
            # Simulate delays
            is_delayed = np.random.random() < 0.25  # 25% delay rate
            if is_delayed:
                delay_days = np.random.exponential(2)
                actual_completion = expected_completion + timedelta(days=delay_days)
            else:
                actual_completion = expected_completion - timedelta(hours=np.random.randint(0, 24))
            
            data.append({
                'service_id': f'SRV-2024-{i:06d}',
                'service_code': np.random.choice(services),
                'service_name': f'Service {i}',
                'category': np.random.choice(categories),
                'district': np.random.choice(districts),
                'mandal': np.random.choice(mandals),
                'submitted_at': submitted_at,
                'current_stage': np.random.choice(stages),
                'sla_days': sla_days,
                'expected_completion': expected_completion,
                'actual_completion': actual_completion
            })
        
        df = pd.DataFrame(data)
        return df

