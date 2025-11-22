from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ServiceStatus(str, Enum):
    """Service request status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class ServiceCategory(str, Enum):
    """Service categories"""
    CATEGORY_A = "CATEGORY_A"
    CATEGORY_B = "CATEGORY_B"
    CATEGORY_C = "CATEGORY_C"


class ServiceRequest(BaseModel):
    """Service request data model"""
    service_id: str = Field(..., description="Unique service request ID")
    service_code: str = Field(..., description="Service type code")
    service_name: str = Field(..., description="Service name")
    category: ServiceCategory = Field(..., description="Service category")
    district: str = Field(..., description="District name")
    mandal: str = Field(..., description="Mandal name")
    citizen_id: Optional[str] = Field(None, description="Citizen ID")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    current_stage: str = Field(..., description="Current workflow stage")
    status: ServiceStatus = Field(..., description="Current status")
    sla_days: int = Field(..., description="SLA in days")
    expected_completion: Optional[datetime] = Field(None, description="Expected completion date")
    actual_completion: Optional[datetime] = Field(None, description="Actual completion date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_id": "SRV-2024-001234",
                "service_code": "CAT-B-001",
                "service_name": "Income Certificate",
                "category": "CATEGORY_B",
                "district": "Visakhapatnam",
                "mandal": "Visakhapatnam Urban",
                "citizen_id": "CIT-12345",
                "submitted_at": "2024-01-15T10:00:00",
                "current_stage": "VRO",
                "status": "IN_PROGRESS",
                "sla_days": 7,
                "expected_completion": "2024-01-22T10:00:00"
            }
        }


class WorkflowTimeline(BaseModel):
    """Workflow stage timeline"""
    stage: str
    entered_at: datetime
    completed_at: Optional[datetime] = None
    duration_hours: Optional[float] = None


class ServiceResponse(BaseModel):
    """Service response with full details"""
    service_id: str
    service_code: str
    service_name: str
    category: ServiceCategory
    district: str
    mandal: str
    status: ServiceStatus
    submitted_at: datetime
    current_stage: str
    sla_days: int
    expected_completion: Optional[datetime]
    actual_completion: Optional[datetime]
    is_delayed: bool
    delay_hours: Optional[float] = None
    delay_percentage: Optional[float] = None
    workflow_timeline: List[WorkflowTimeline] = []
    prediction: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_id": "SRV-2024-001234",
                "service_code": "CAT-B-001",
                "service_name": "Income Certificate",
                "category": "CATEGORY_B",
                "district": "Visakhapatnam",
                "mandal": "Visakhapatnam Urban",
                "status": "DELAYED",
                "submitted_at": "2024-01-15T10:00:00",
                "current_stage": "VRO",
                "sla_days": 7,
                "expected_completion": "2024-01-22T10:00:00",
                "actual_completion": None,
                "is_delayed": True,
                "delay_hours": 48.5,
                "delay_percentage": 28.9
            }
        }

