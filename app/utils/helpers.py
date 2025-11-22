"""
Helper utility functions
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_delay_metrics(service_data: Dict) -> Dict:
    """Calculate delay metrics for a service"""
    try:
        submitted_at = service_data.get('submitted_at')
        expected_completion = service_data.get('expected_completion')
        actual_completion = service_data.get('actual_completion')
        sla_days = service_data.get('sla_days', 7)
        
        if not submitted_at:
            return {}
        
        if isinstance(submitted_at, str):
            submitted_at = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
        if isinstance(expected_completion, str):
            expected_completion = datetime.fromisoformat(expected_completion.replace('Z', '+00:00'))
        if actual_completion and isinstance(actual_completion, str):
            actual_completion = datetime.fromisoformat(actual_completion.replace('Z', '+00:00'))
        
        metrics = {
            'is_delayed': False,
            'delay_hours': 0.0,
            'delay_percentage': 0.0,
            'days_remaining': 0
        }
        
        now = datetime.now()
        
        if actual_completion:
            if actual_completion > expected_completion:
                delay = (actual_completion - expected_completion).total_seconds() / 3600
                metrics['is_delayed'] = True
                metrics['delay_hours'] = delay
                metrics['delay_percentage'] = (delay / (sla_days * 24)) * 100
        else:
            # For ongoing services
            if now > expected_completion:
                delay = (now - expected_completion).total_seconds() / 3600
                metrics['is_delayed'] = True
                metrics['delay_hours'] = delay
                metrics['delay_percentage'] = (delay / (sla_days * 24)) * 100
            else:
                remaining = (expected_completion - now).total_seconds() / 86400
                metrics['days_remaining'] = max(0, remaining)
        
        return metrics
    except Exception as e:
        logger.error(f"Error calculating delay metrics: {e}")
        return {}


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime string"""
    try:
        if isinstance(dt_str, datetime):
            return dt_str
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return None

