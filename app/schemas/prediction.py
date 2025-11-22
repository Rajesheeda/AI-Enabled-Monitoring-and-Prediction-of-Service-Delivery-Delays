from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request for delay prediction"""
    service_id: Optional[str] = Field(None, description="Specific service ID")
    service_code: Optional[str] = Field(None, description="Service type code")
    district: Optional[str] = Field(None, description="Filter by district")
    mandal: Optional[str] = Field(None, description="Filter by mandal")
    category: Optional[str] = Field(None, description="Filter by category")
    prediction_horizon_days: int = Field(7, description="Days ahead to predict", ge=1, le=30)
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_code": "CAT-B-001",
                "district": "Visakhapatnam",
                "prediction_horizon_days": 7
            }
        }


class DelayPrediction(BaseModel):
    """Individual delay prediction"""
    service_id: str
    service_code: str
    service_name: str
    district: str
    mandal: str
    current_stage: str
    predicted_delay_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of delay")
    predicted_completion_date: datetime
    expected_completion_date: datetime
    predicted_delay_hours: float
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    contributing_factors: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_id": "SRV-2024-001234",
                "service_code": "CAT-B-001",
                "service_name": "Income Certificate",
                "district": "Visakhapatnam",
                "mandal": "Visakhapatnam Urban",
                "current_stage": "VRO",
                "predicted_delay_probability": 0.75,
                "predicted_completion_date": "2024-01-25T10:00:00",
                "expected_completion_date": "2024-01-22T10:00:00",
                "predicted_delay_hours": 72.0,
                "confidence_score": 0.82,
                "risk_level": "HIGH",
                "contributing_factors": ["High workload at VRO stage", "Historical delays in district"]
            }
        }


class PredictionResponse(BaseModel):
    """Response containing predictions"""
    predictions: List[DelayPrediction]
    total_predictions: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    generated_at: datetime
    model_version: str
    summary: Dict[str, any] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [],
                "total_predictions": 150,
                "high_risk_count": 25,
                "medium_risk_count": 45,
                "low_risk_count": 80,
                "generated_at": "2024-01-20T10:00:00",
                "model_version": "v1.0.0",
                "summary": {
                    "average_delay_probability": 0.35,
                    "total_predicted_delays": 70
                }
            }
        }

