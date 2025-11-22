"""
Dashboard API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from datetime import datetime, timedelta
import logging

from app.services.service_manager import ServiceManager
from app.services.analytics_service import AnalyticsService
from app.services.prediction_service import PredictionService
from app.schemas.analytics import AnalyticsRequest

logger = logging.getLogger(__name__)

router = APIRouter()

def get_service_manager():
    return ServiceManager()

def get_analytics_service():
    return AnalyticsService()

def get_prediction_service():
    return PredictionService()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    service_manager: ServiceManager = Depends(get_service_manager),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Get dashboard summary data"""
    try:
        services = service_manager.get_all_services()
        
        # Get analytics
        analytics_request = AnalyticsRequest(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        analytics = analytics_service.analyze(analytics_request, services)
        
        # Get predictions
        from app.schemas.prediction import PredictionRequest
        prediction_request = PredictionRequest()
        predictions = prediction_service.predict(prediction_request, services)
        
        # Calculate summary metrics
        total_services = len(services)
        active_services = sum(1 for s in services if s.get('status') not in ['COMPLETED', 'CANCELLED'])
        
        summary = {
            "total_services": total_services,
            "active_services": active_services,
            "completed_services": total_services - active_services,
            "sla_compliance": analytics.overall_sla_compliance,
            "average_tat_hours": analytics.average_tat_hours,
            "total_delayed": analytics.total_delayed,
            "high_risk_predictions": predictions.high_risk_count,
            "medium_risk_predictions": predictions.medium_risk_count,
            "low_risk_predictions": predictions.low_risk_count,
            "last_updated": datetime.now().isoformat()
        }
        
        return summary
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/trends")
async def get_dashboard_trends(
    days: int = 30,
    service_manager: ServiceManager = Depends(get_service_manager),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get trend data for dashboard"""
    try:
        services = service_manager.get_all_services()
        
        analytics_request = AnalyticsRequest(
            start_date=datetime.now() - timedelta(days=days),
            end_date=datetime.now()
        )
        analytics = analytics_service.analyze(analytics_request, services)
        
        return {
            "trends": analytics.trends,
            "root_cause": analytics.root_cause_analysis.dict(),
            "period_start": analytics.period_start.isoformat(),
            "period_end": analytics.period_end.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/hotspots")
async def get_dashboard_hotspots(
    service_manager: ServiceManager = Depends(get_service_manager),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get delay hotspots for dashboard"""
    try:
        services = service_manager.get_all_services()
        
        analytics_request = AnalyticsRequest(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        analytics = analytics_service.analyze(analytics_request, services)
        
        return {
            "district_hotspots": [d.dict() for d in analytics.root_cause_analysis.district_hotspots],
            "stage_bottlenecks": [s.dict() for s in analytics.root_cause_analysis.stage_bottlenecks],
            "primary_causes": analytics.root_cause_analysis.primary_causes,
            "recommendations": analytics.root_cause_analysis.recommendations
        }
    except Exception as e:
        logger.error(f"Error getting dashboard hotspots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

