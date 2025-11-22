from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class WorkflowStage(str, Enum):
    """Workflow stage enumeration"""
    APPLICATION = "APPLICATION"
    VRO = "VRO"
    REVENUE_INSPECTOR = "REVENUE_INSPECTOR"
    TAHSILDAR = "TAHSILDAR"
    FINAL_PROCESSING = "FINAL_PROCESSING"
    DELIVERED = "DELIVERED"


class WorkflowStatus(BaseModel):
    """Workflow status tracking"""
    service_id: str
    current_stage: WorkflowStage
    stage_entered_at: datetime
    previous_stage: Optional[WorkflowStage] = None
    stage_duration_hours: Optional[float] = None
    is_stalled: bool = Field(False, description="If stage duration exceeds threshold")
    next_expected_stage: Optional[WorkflowStage] = None
    estimated_stage_completion: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_id": "SRV-2024-001234",
                "current_stage": "VRO",
                "stage_entered_at": "2024-01-16T10:00:00",
                "previous_stage": "APPLICATION",
                "stage_duration_hours": 24.5,
                "is_stalled": False,
                "next_expected_stage": "REVENUE_INSPECTOR",
                "estimated_stage_completion": "2024-01-17T14:00:00"
            }
        }

