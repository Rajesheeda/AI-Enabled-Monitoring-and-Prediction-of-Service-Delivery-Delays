"""
Prediction API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService
from app.services.service_manager import ServiceManager

logger = logging.getLogger(__name__)

router = APIRouter()

def get_prediction_service():
    return PredictionService()

def get_service_manager():
    return ServiceManager()

@router.post("/predict", response_model=PredictionResponse)
async def predict_delays(
    request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """Predict delays for services"""
    try:
        # Get all services
        services = service_manager.get_all_services()
        
        if not services:
            raise HTTPException(status_code=404, detail="No services found")
        
        # Generate predictions
        response = prediction_service.predict(request, services)
        
        return response
    except Exception as e:
        logger.error(f"Error in prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{service_id}", response_model=PredictionResponse)
async def predict_single_service(
    service_id: str,
    prediction_service: PredictionService = Depends(get_prediction_service),
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """Predict delay for a single service"""
    try:
        service = service_manager.get_service(service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
        
        request = PredictionRequest(service_id=service_id)
        response = prediction_service.predict(request, [service])
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in single prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

