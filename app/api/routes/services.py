"""
Service Management API Routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.schemas.service import ServiceRequest, ServiceResponse
from app.services.service_manager import ServiceManager

logger = logging.getLogger(__name__)

router = APIRouter()

def get_service_manager():
    return ServiceManager()

@router.post("/services", response_model=dict)
async def create_service(
    service: ServiceRequest,
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """Create a new service request"""
    try:
        service_data = service.dict()
        created = service_manager.add_service(service_data)
        return {"message": "Service created successfully", "service": created}
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services", response_model=List[dict])
async def list_services(
    district: Optional[str] = Query(None),
    mandal: Optional[str] = Query(None),
    service_code: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """List all services with optional filters"""
    try:
        filters = {}
        if district:
            filters['district'] = district
        if mandal:
            filters['mandal'] = mandal
        if service_code:
            filters['service_code'] = service_code
        if category:
            filters['category'] = category
        if status:
            filters['status'] = status
        
        services = service_manager.list_services(filters)
        return services
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}", response_model=dict)
async def get_service(
    service_id: str,
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """Get a specific service by ID"""
    try:
        service = service_manager.get_service(service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
        
        return service
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/services/{service_id}", response_model=dict)
async def update_service(
    service_id: str,
    updates: dict,
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """Update a service"""
    try:
        updated = service_manager.update_service(service_id, updates)
        
        if not updated:
            raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
        
        return {"message": "Service updated successfully", "service": updated}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

