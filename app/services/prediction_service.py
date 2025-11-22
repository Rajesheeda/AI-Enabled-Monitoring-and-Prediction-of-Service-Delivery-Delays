"""
Prediction Service
Handles delay prediction business logic
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from app.models.predictor import DelayPredictor
from app.schemas.prediction import PredictionRequest, PredictionResponse, DelayPrediction
from app.schemas.service import ServiceRequest, ServiceResponse

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for delay predictions"""
    
    def __init__(self):
        self.predictor = DelayPredictor()
    
    def predict(self, request: PredictionRequest, services: List[Dict]) -> PredictionResponse:
        """Generate predictions for services"""
        try:
            # Filter services based on request
            filtered_services = self._filter_services(services, request)
            
            predictions = []
            for service in filtered_services:
                prediction_data = self.predictor.predict_delay(service)
                
                # Determine risk level
                risk_level = prediction_data.get('risk_level', 'LOW')
                
                prediction = DelayPrediction(
                    service_id=service.get('service_id', ''),
                    service_code=service.get('service_code', ''),
                    service_name=service.get('service_name', ''),
                    district=service.get('district', ''),
                    mandal=service.get('mandal', ''),
                    current_stage=service.get('current_stage', ''),
                    predicted_delay_probability=prediction_data['predicted_delay_probability'],
                    predicted_completion_date=datetime.fromisoformat(prediction_data['predicted_completion_date']),
                    expected_completion_date=datetime.fromisoformat(prediction_data['expected_completion_date']),
                    predicted_delay_hours=prediction_data['predicted_delay_hours'],
                    confidence_score=prediction_data['confidence_score'],
                    risk_level=risk_level,
                    contributing_factors=prediction_data['contributing_factors']
                )
                predictions.append(prediction)
            
            # Calculate summary statistics
            high_risk = sum(1 for p in predictions if p.risk_level in ['HIGH', 'CRITICAL'])
            medium_risk = sum(1 for p in predictions if p.risk_level == 'MEDIUM')
            low_risk = sum(1 for p in predictions if p.risk_level == 'LOW')
            
            avg_delay_prob = sum(p.predicted_delay_probability for p in predictions) / len(predictions) if predictions else 0
            total_predicted_delays = sum(1 for p in predictions if p.predicted_delay_probability > 0.5)
            
            summary = {
                'average_delay_probability': avg_delay_prob,
                'total_predicted_delays': total_predicted_delays,
                'prediction_horizon_days': request.prediction_horizon_days
            }
            
            return PredictionResponse(
                predictions=predictions,
                total_predictions=len(predictions),
                high_risk_count=high_risk,
                medium_risk_count=medium_risk,
                low_risk_count=low_risk,
                generated_at=datetime.now(),
                model_version=self.predictor.model_version,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            raise
    
    def _filter_services(self, services: List[Dict], request: PredictionRequest) -> List[Dict]:
        """Filter services based on request criteria"""
        filtered = services
        
        if request.service_id:
            filtered = [s for s in filtered if s.get('service_id') == request.service_id]
        
        if request.service_code:
            filtered = [s for s in filtered if s.get('service_code') == request.service_code]
        
        if request.district:
            filtered = [s for s in filtered if s.get('district') == request.district]
        
        if request.mandal:
            filtered = [s for s in filtered if s.get('mandal') == request.mandal]
        
        if request.category:
            filtered = [s for s in filtered if s.get('category') == request.category]
        
        return filtered
    
    def predict_single(self, service_data: Dict) -> Dict:
        """Predict delay for a single service"""
        return self.predictor.predict_delay(service_data)

