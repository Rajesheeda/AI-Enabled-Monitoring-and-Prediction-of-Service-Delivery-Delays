"""
Analytics API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.schemas.analytics import AnalyticsRequest, AnalyticsResponse
from app.services.analytics_service import AnalyticsService
from app.services.service_manager import ServiceManager

logger = logging.getLogger(__name__)

router = APIRouter()

def get_analytics_service():
    return AnalyticsService()

def get_service_manager():
    return ServiceManager()

@router.post("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    request: AnalyticsRequest,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """Get analytics and insights"""
    try:
        services = service_manager.get_all_services()
        
        if not services:
            raise HTTPException(status_code=404, detail="No services found")
        
        response = analytics_service.analyze(request, services)
        
        return response
    except Exception as e:
        logger.error(f"Error in analytics endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/root-cause", response_model=AnalyticsResponse)
async def get_root_cause_analysis(
    district: str = None,
    mandal: str = None,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """Get root cause analysis"""
    try:
        from datetime import datetime, timedelta
        
        request = AnalyticsRequest(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            district=district,
            mandal=mandal
        )
        
        services = service_manager.get_all_services()
        response = analytics_service.analyze(request, services)
        
        return response
    except Exception as e:
        logger.error(f"Error in root cause analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

