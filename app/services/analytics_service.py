"""
Analytics Service
Provides root cause analysis and performance insights
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import logging

from app.schemas.analytics import (
    AnalyticsRequest, AnalyticsResponse, RootCauseAnalysis,
    StageDelayMetrics, DistrictMetrics, ServiceMetrics
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and root cause analysis"""
    
    def analyze(self, request: AnalyticsRequest, services: List[Dict]) -> AnalyticsResponse:
        """Perform comprehensive analytics"""
        try:
            # Filter services
            filtered_services = self._filter_services(services, request)
            
            if not filtered_services:
                return self._empty_response(request)
            
            df = pd.DataFrame(filtered_services)
            
            # Convert datetime columns
            datetime_cols = ['submitted_at', 'expected_completion', 'actual_completion']
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Calculate metrics
            total_services = len(df)
            df['is_delayed'] = (df['actual_completion'] > df['expected_completion']).fillna(False)
            total_delayed = df['is_delayed'].sum()
            
            df['tat_hours'] = (df['actual_completion'] - df['submitted_at']).dt.total_seconds() / 3600
            avg_tat = df['tat_hours'].mean() if not df['tat_hours'].isna().all() else 0
            
            sla_compliance = ((total_services - total_delayed) / total_services * 100) if total_services > 0 else 0
            
            # Root cause analysis
            root_cause = self._root_cause_analysis(df)
            
            # Trends
            trends = self._calculate_trends(df)
            
            start_date = request.start_date or df['submitted_at'].min() if 'submitted_at' in df.columns else datetime.now()
            end_date = request.end_date or df['submitted_at'].max() if 'submitted_at' in df.columns else datetime.now()
            
            return AnalyticsResponse(
                period_start=start_date,
                period_end=end_date,
                total_services=total_services,
                total_delayed=int(total_delayed),
                overall_sla_compliance=float(sla_compliance),
                average_tat_hours=float(avg_tat),
                root_cause_analysis=root_cause,
                trends=trends,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in analytics: {e}")
            raise
    
    def _filter_services(self, services: List[Dict], request: AnalyticsRequest) -> List[Dict]:
        """Filter services based on request"""
        filtered = services
        
        if request.district:
            filtered = [s for s in filtered if s.get('district') == request.district]
        
        if request.mandal:
            filtered = [s for s in filtered if s.get('mandal') == request.mandal]
        
        if request.service_code:
            filtered = [s for s in filtered if s.get('service_code') == request.service_code]
        
        if request.category:
            filtered = [s for s in filtered if s.get('category') == request.category]
        
        if request.workflow_stage:
            filtered = [s for s in filtered if s.get('current_stage') == request.workflow_stage]
        
        # Date filtering
        if request.start_date or request.end_date:
            filtered = [s for s in filtered if self._in_date_range(s, request.start_date, request.end_date)]
        
        return filtered
    
    def _in_date_range(self, service: Dict, start: Optional[datetime], end: Optional[datetime]) -> bool:
        """Check if service is in date range"""
        submitted = service.get('submitted_at')
        if not submitted:
            return True
        
        if isinstance(submitted, str):
            submitted = pd.to_datetime(submitted, errors='coerce')
        
        if start and submitted < start:
            return False
        if end and submitted > end:
            return False
        
        return True
    
    def _root_cause_analysis(self, df: pd.DataFrame) -> RootCauseAnalysis:
        """Perform root cause analysis"""
        try:
            # Stage bottlenecks
            stage_metrics = []
            if 'current_stage' in df.columns:
                for stage in df['current_stage'].unique():
                    stage_df = df[df['current_stage'] == stage]
                    total = len(stage_df)
                    delayed = stage_df['is_delayed'].sum()
                    delay_pct = (delayed / total * 100) if total > 0 else 0
                    avg_delay = stage_df[stage_df['is_delayed']]['tat_hours'].mean() if delayed > 0 else 0
                    
                    stage_metrics.append(StageDelayMetrics(
                        stage=str(stage),
                        total_requests=total,
                        delayed_requests=int(delayed),
                        delay_percentage=float(delay_pct),
                        average_delay_hours=float(avg_delay) if not pd.isna(avg_delay) else 0,
                        median_delay_hours=float(stage_df[stage_df['is_delayed']]['tat_hours'].median()) if delayed > 0 else 0,
                        max_delay_hours=float(stage_df[stage_df['is_delayed']]['tat_hours'].max()) if delayed > 0 else 0
                    ))
            
            # District hotspots
            district_metrics = []
            if 'district' in df.columns:
                for district in df['district'].unique():
                    dist_df = df[df['district'] == district]
                    total = len(dist_df)
                    delayed = dist_df['is_delayed'].sum()
                    compliance = ((total - delayed) / total * 100) if total > 0 else 0
                    avg_tat = dist_df['tat_hours'].mean() if not dist_df['tat_hours'].isna().all() else 0
                    
                    # Calculate trend (simplified)
                    trend = "STABLE"
                    if len(dist_df) > 10:
                        recent = dist_df.tail(5)['is_delayed'].mean()
                        older = dist_df.head(5)['is_delayed'].mean()
                        if recent > older * 1.1:
                            trend = "INCREASING"
                        elif recent < older * 0.9:
                            trend = "DECREASING"
                    
                    district_metrics.append(DistrictMetrics(
                        district=str(district),
                        total_services=total,
                        completed_on_time=int(total - delayed),
                        delayed_services=int(delayed),
                        sla_compliance_percentage=float(compliance),
                        average_tat_hours=float(avg_tat) if not pd.isna(avg_tat) else 0,
                        delay_trend=trend
                    ))
            
            # Service trends
            service_metrics = []
            if 'service_code' in df.columns:
                for service_code in df['service_code'].unique():
                    svc_df = df[df['service_code'] == service_code]
                    total = len(svc_df)
                    delayed = svc_df['is_delayed'].sum()
                    delay_rate = (delayed / total) if total > 0 else 0
                    compliance = ((total - delayed) / total * 100) if total > 0 else 0
                    avg_tat = svc_df['tat_hours'].mean() if not svc_df['tat_hours'].isna().all() else 0
                    
                    service_metrics.append(ServiceMetrics(
                        service_code=str(service_code),
                        service_name=str(svc_df['service_name'].iloc[0]) if 'service_name' in svc_df.columns else '',
                        total_requests=total,
                        average_completion_hours=float(avg_tat) if not pd.isna(avg_tat) else 0,
                        delay_rate=float(delay_rate),
                        sla_compliance_percentage=float(compliance)
                    ))
            
            # Primary causes
            primary_causes = []
            if stage_metrics:
                top_stage = max(stage_metrics, key=lambda x: x.delay_percentage)
                primary_causes.append({
                    'cause': f'High delays at {top_stage.stage} stage',
                    'impact_percentage': top_stage.delay_percentage,
                    'affected_services': top_stage.delayed_requests
                })
            
            if district_metrics:
                top_district = max(district_metrics, key=lambda x: x.delayed_services)
                primary_causes.append({
                    'cause': f'High delays in {top_district.district} district',
                    'impact_percentage': (top_district.delayed_services / len(df) * 100) if len(df) > 0 else 0,
                    'affected_services': top_district.delayed_services
                })
            
            # Recommendations
            recommendations = []
            if stage_metrics:
                bottleneck = max(stage_metrics, key=lambda x: x.delay_percentage)
                if bottleneck.delay_percentage > 20:
                    recommendations.append(f"Increase staffing/resources at {bottleneck.stage} stage")
            
            if district_metrics:
                hotspot = max(district_metrics, key=lambda x: x.delayed_services)
                if hotspot.sla_compliance_percentage < 80:
                    recommendations.append(f"Implement workload balancing in {hotspot.district} district")
            
            return RootCauseAnalysis(
                primary_causes=primary_causes,
                stage_bottlenecks=stage_metrics,
                district_hotspots=district_metrics,
                service_trends=service_metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in root cause analysis: {e}")
            return RootCauseAnalysis(
                primary_causes=[],
                stage_bottlenecks=[],
                district_hotspots=[],
                service_trends=[],
                recommendations=[]
            )
    
    def _calculate_trends(self, df: pd.DataFrame) -> Dict:
        """Calculate trend metrics"""
        try:
            trends = {}
            
            if 'submitted_at' in df.columns and len(df) > 0:
                df_sorted = df.sort_values('submitted_at')
                df_sorted['month'] = df_sorted['submitted_at'].dt.to_period('M')
                
                monthly = df_sorted.groupby('month').agg({
                    'is_delayed': ['sum', 'count']
                }).reset_index()
                
                if len(monthly) > 1:
                    recent_delay_rate = monthly['is_delayed']['sum'].iloc[-1] / monthly['is_delayed']['count'].iloc[-1]
                    older_delay_rate = monthly['is_delayed']['sum'].iloc[0] / monthly['is_delayed']['count'].iloc[0]
                    
                    trends['delay_trend'] = 'INCREASING' if recent_delay_rate > older_delay_rate else 'DECREASING'
                    trends['delay_rate_change'] = float((recent_delay_rate - older_delay_rate) * 100)
            
            return trends
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
    
    def _empty_response(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """Return empty response when no data"""
        start = request.start_date or datetime.now() - timedelta(days=30)
        end = request.end_date or datetime.now()
        
        return AnalyticsResponse(
            period_start=start,
            period_end=end,
            total_services=0,
            total_delayed=0,
            overall_sla_compliance=0.0,
            average_tat_hours=0.0,
            root_cause_analysis=RootCauseAnalysis(
                primary_causes=[],
                stage_bottlenecks=[],
                district_hotspots=[],
                service_trends=[],
                recommendations=[]
            ),
            trends={},
            generated_at=datetime.now()
        )

