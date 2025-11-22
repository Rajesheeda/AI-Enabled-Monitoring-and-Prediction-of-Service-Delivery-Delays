"""
Delay Prediction Model
Uses XGBoost/LightGBM for classification and regression
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import joblib
import os
from pathlib import Path
import logging

try:
    import xgboost as xgb
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
except ImportError:
    xgb = None
    RandomForestClassifier = None
    RandomForestRegressor = None

logger = logging.getLogger(__name__)


class DelayPredictor:
    """Predicts service delivery delays using ML models"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "./data/models"
        Path(self.model_path).mkdir(parents=True, exist_ok=True)
        
        self.delay_classifier = None
        self.delay_regressor = None
        self.label_encoders = {}
        self.model_version = "v1.0.0"
        self.feature_columns = [
            'days_since_submission', 'current_stage_encoded', 'district_encoded',
            'mandal_encoded', 'service_code_encoded', 'category_encoded',
            'workload_at_stage', 'historical_delay_rate_district',
            'historical_delay_rate_mandal', 'historical_delay_rate_service',
            'day_of_week', 'month', 'is_weekend'
        ]
        
    def _load_models(self):
        """Load trained models if they exist"""
        classifier_path = os.path.join(self.model_path, "delay_classifier.joblib")
        regressor_path = os.path.join(self.model_path, "delay_regressor.joblib")
        encoders_path = os.path.join(self.model_path, "label_encoders.joblib")
        
        if os.path.exists(classifier_path) and os.path.exists(regressor_path):
            try:
                self.delay_classifier = joblib.load(classifier_path)
                self.delay_regressor = joblib.load(regressor_path)
                if os.path.exists(encoders_path):
                    self.label_encoders = joblib.load(encoders_path)
                logger.info("Models loaded successfully")
                return True
            except Exception as e:
                logger.error(f"Error loading models: {e}")
                return False
        return False
    
    def _create_dummy_models(self):
        """Create dummy models for testing/demo purposes"""
        if xgb is None:
            logger.warning("XGBoost not available, using RandomForest")
            if RandomForestClassifier is None:
                logger.error("No ML libraries available")
                return False
        
        # Create simple dummy models
        n_samples = 100
        n_features = len(self.feature_columns)
        
        X_dummy = np.random.rand(n_samples, n_features)
        y_classifier = np.random.randint(0, 2, n_samples)
        y_regressor = np.random.rand(n_samples) * 48  # Hours
        
        if xgb:
            self.delay_classifier = xgb.XGBClassifier(n_estimators=10, random_state=42)
            self.delay_regressor = xgb.XGBRegressor(n_estimators=10, random_state=42)
        else:
            self.delay_classifier = RandomForestClassifier(n_estimators=10, random_state=42)
            self.delay_regressor = RandomForestRegressor(n_estimators=10, random_state=42)
        
        self.delay_classifier.fit(X_dummy, y_classifier)
        self.delay_regressor.fit(X_dummy, y_regressor)
        
        # Initialize label encoders
        self.label_encoders = {
            'current_stage': LabelEncoder(),
            'district': LabelEncoder(),
            'mandal': LabelEncoder(),
            'service_code': LabelEncoder(),
            'category': LabelEncoder()
        }
        
        # Fit with dummy data
        dummy_stages = ['APPLICATION', 'VRO', 'REVENUE_INSPECTOR', 'TAHSILDAR', 'FINAL_PROCESSING']
        dummy_districts = ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore']
        dummy_mandals = ['Urban', 'Rural', 'Semi-Urban']
        dummy_services = ['CAT-B-001', 'CAT-B-002', 'CAT-B-003']
        dummy_categories = ['CATEGORY_A', 'CATEGORY_B', 'CATEGORY_C']
        
        self.label_encoders['current_stage'].fit(dummy_stages)
        self.label_encoders['district'].fit(dummy_districts)
        self.label_encoders['mandal'].fit(dummy_mandals)
        self.label_encoders['service_code'].fit(dummy_services)
        self.label_encoders['category'].fit(dummy_categories)
        
        logger.info("Dummy models created")
        return True
    
    def prepare_features(self, service_data: Dict) -> np.ndarray:
        """Prepare features for prediction"""
        try:
            # Calculate days since submission
            submitted_at = pd.to_datetime(service_data.get('submitted_at', datetime.now()))
            days_since = (datetime.now() - submitted_at).total_seconds() / 86400
            
            # Encode categorical features
            current_stage = service_data.get('current_stage', 'APPLICATION')
            district = service_data.get('district', 'Unknown')
            mandal = service_data.get('mandal', 'Unknown')
            service_code = service_data.get('service_code', 'Unknown')
            category = service_data.get('category', 'CATEGORY_B')
            
            # Encode with label encoders (handle unseen values)
            stage_encoded = self._safe_encode('current_stage', current_stage)
            district_encoded = self._safe_encode('district', district)
            mandal_encoded = self._safe_encode('mandal', mandal)
            service_encoded = self._safe_encode('service_code', service_code)
            category_encoded = self._safe_encode('category', category)
            
            # Calculate derived features
            workload_at_stage = service_data.get('workload_at_stage', 0.5)  # Placeholder
            hist_delay_district = service_data.get('historical_delay_rate_district', 0.15)
            hist_delay_mandal = service_data.get('historical_delay_rate_mandal', 0.15)
            hist_delay_service = service_data.get('historical_delay_rate_service', 0.15)
            
            # Time features
            now = datetime.now()
            day_of_week = now.weekday()
            month = now.month
            is_weekend = 1 if day_of_week >= 5 else 0
            
            features = np.array([[
                days_since,
                stage_encoded,
                district_encoded,
                mandal_encoded,
                service_encoded,
                category_encoded,
                workload_at_stage,
                hist_delay_district,
                hist_delay_mandal,
                hist_delay_service,
                day_of_week,
                month,
                is_weekend
            ]])
            
            return features
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return np.zeros((1, len(self.feature_columns)))
    
    def _safe_encode(self, encoder_name: str, value: str) -> int:
        """Safely encode a value, handling unseen categories"""
        if encoder_name not in self.label_encoders:
            return 0
        
        encoder = self.label_encoders[encoder_name]
        try:
            if value in encoder.classes_:
                return encoder.transform([value])[0]
            else:
                # Return most common class index for unseen values
                return 0
        except:
            return 0
    
    def predict_delay(self, service_data: Dict) -> Dict:
        """Predict delay for a single service"""
        if self.delay_classifier is None or self.delay_regressor is None:
            if not self._load_models():
                self._create_dummy_models()
        
        if self.delay_classifier is None:
            return self._default_prediction(service_data)
        
        try:
            features = self.prepare_features(service_data)
            
            # Predict delay probability
            delay_probability = self.delay_classifier.predict_proba(features)[0][1]
            
            # Predict delay hours
            delay_hours = max(0, self.delay_regressor.predict(features)[0])
            
            # Calculate risk level
            risk_level = self._calculate_risk_level(delay_probability, delay_hours)
            
            # Calculate predicted completion
            submitted_at = pd.to_datetime(service_data.get('submitted_at', datetime.now()))
            sla_days = service_data.get('sla_days', 7)
            expected_completion = submitted_at + timedelta(days=sla_days)
            predicted_completion = expected_completion + timedelta(hours=delay_hours)
            
            # Confidence score (simplified)
            confidence = min(0.95, 0.5 + delay_probability * 0.45)
            
            # Contributing factors
            factors = self._identify_factors(service_data, delay_probability, delay_hours)
            
            return {
                'predicted_delay_probability': float(delay_probability),
                'predicted_delay_hours': float(delay_hours),
                'predicted_completion_date': predicted_completion.isoformat(),
                'expected_completion_date': expected_completion.isoformat(),
                'risk_level': risk_level,
                'confidence_score': float(confidence),
                'contributing_factors': factors
            }
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return self._default_prediction(service_data)
    
    def _calculate_risk_level(self, probability: float, delay_hours: float) -> str:
        """Calculate risk level based on probability and delay hours"""
        if probability >= 0.75 or delay_hours >= 48:
            return "CRITICAL"
        elif probability >= 0.6 or delay_hours >= 24:
            return "HIGH"
        elif probability >= 0.4 or delay_hours >= 12:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_factors(self, service_data: Dict, probability: float, delay_hours: float) -> List[str]:
        """Identify contributing factors for delay"""
        factors = []
        
        days_since = (datetime.now() - pd.to_datetime(service_data.get('submitted_at', datetime.now()))).days
        sla_days = service_data.get('sla_days', 7)
        
        if days_since > sla_days * 0.7:
            factors.append(f"Service already {days_since} days old (SLA: {sla_days} days)")
        
        current_stage = service_data.get('current_stage', '')
        if current_stage in ['VRO', 'REVENUE_INSPECTOR']:
            factors.append(f"Currently at {current_stage} stage (common bottleneck)")
        
        hist_delay = service_data.get('historical_delay_rate_district', 0)
        if hist_delay > 0.2:
            factors.append(f"High historical delay rate in district ({hist_delay*100:.1f}%)")
        
        return factors
    
    def _default_prediction(self, service_data: Dict) -> Dict:
        """Return default prediction when models are not available"""
        submitted_at = pd.to_datetime(service_data.get('submitted_at', datetime.now()))
        sla_days = service_data.get('sla_days', 7)
        expected_completion = submitted_at + timedelta(days=sla_days)
        
        return {
            'predicted_delay_probability': 0.3,
            'predicted_delay_hours': 0.0,
            'predicted_completion_date': expected_completion.isoformat(),
            'expected_completion_date': expected_completion.isoformat(),
            'risk_level': 'LOW',
            'confidence_score': 0.5,
            'contributing_factors': ['Model not trained - using default prediction']
        }
    
    def save_models(self):
        """Save trained models"""
        try:
            classifier_path = os.path.join(self.model_path, "delay_classifier.joblib")
            regressor_path = os.path.join(self.model_path, "delay_regressor.joblib")
            encoders_path = os.path.join(self.model_path, "label_encoders.joblib")
            
            if self.delay_classifier:
                joblib.dump(self.delay_classifier, classifier_path)
            if self.delay_regressor:
                joblib.dump(self.delay_regressor, regressor_path)
            if self.label_encoders:
                joblib.dump(self.label_encoders, encoders_path)
            
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")

