from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class AnalyticsRequest(BaseModel):
    """Request for analytics and insights"""
    start_date: Optional[datetime] = Field(None, description="Start date for analysis")
    end_date: Optional[datetime] = Field(None, description="End date for analysis")
    district: Optional[str] = Field(None, description="Filter by district")
    mandal: Optional[str] = Field(None, description="Filter by mandal")
    service_code: Optional[str] = Field(None, description="Filter by service code")
    category: Optional[str] = Field(None, description="Filter by category")
    workflow_stage: Optional[str] = Field(None, description="Filter by workflow stage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-01-31T23:59:59",
                "district": "Visakhapatnam"
            }
        }


class StageDelayMetrics(BaseModel):
    """Delay metrics for a workflow stage"""
    stage: str
    total_requests: int
    delayed_requests: int
    delay_percentage: float
    average_delay_hours: float
    median_delay_hours: float
    max_delay_hours: float


class DistrictMetrics(BaseModel):
    """Performance metrics for a district"""
    district: str
    total_services: int
    completed_on_time: int
    delayed_services: int
    sla_compliance_percentage: float
    average_tat_hours: float
    delay_trend: str = Field(..., description="INCREASING, DECREASING, STABLE")


class ServiceMetrics(BaseModel):
    """Performance metrics for a service type"""
    service_code: str
    service_name: str
    total_requests: int
    average_completion_hours: float
    delay_rate: float
    sla_compliance_percentage: float


class RootCauseAnalysis(BaseModel):
    """Root cause analysis results"""
    primary_causes: List[Dict[str, any]] = Field(..., description="Top root causes")
    stage_bottlenecks: List[StageDelayMetrics] = Field(..., description="Bottleneck stages")
    district_hotspots: List[DistrictMetrics] = Field(..., description="High-delay districts")
    service_trends: List[ServiceMetrics] = Field(..., description="Service-level trends")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "primary_causes": [
                    {
                        "cause": "High workload at VRO stage",
                        "impact_percentage": 35.5,
                        "affected_services": 1250
                    }
                ],
                "stage_bottlenecks": [],
                "district_hotspots": [],
                "service_trends": [],
                "recommendations": [
                    "Increase staffing at VRO stage in Visakhapatnam district",
                    "Implement workload balancing across mandals"
                ]
            }
        }


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    period_start: datetime
    period_end: datetime
    total_services: int
    total_delayed: int
    overall_sla_compliance: float
    average_tat_hours: float
    root_cause_analysis: RootCauseAnalysis
    trends: Dict[str, any] = {}
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2024-01-01T00:00:00",
                "period_end": "2024-01-31T23:59:59",
                "total_services": 5000,
                "total_delayed": 750,
                "overall_sla_compliance": 85.0,
                "average_tat_hours": 120.5,
                "root_cause_analysis": {},
                "trends": {},
                "generated_at": "2024-02-01T10:00:00"
            }
        }

