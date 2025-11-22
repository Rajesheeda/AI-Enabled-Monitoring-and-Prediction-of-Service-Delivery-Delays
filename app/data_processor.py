"""
Data Processing Pipeline
Processes historical and real-time service data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from pathlib import Path
import json

from app.services.service_manager import ServiceManager
from app.utils.helpers import calculate_delay_metrics

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes service delivery data"""
    
    def __init__(self, service_manager: Optional[ServiceManager] = None):
        self.service_manager = service_manager or ServiceManager()
        self.processed_data_path = Path("./data/processed")
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
    
    def process_historical_data(self, data: List[Dict]) -> pd.DataFrame:
        """Process historical service data"""
        try:
            df = pd.DataFrame(data)
            
            # Convert datetime columns
            datetime_cols = ['submitted_at', 'expected_completion', 'actual_completion']
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Calculate delay metrics
            df['is_delayed'] = (df['actual_completion'] > df['expected_completion']).fillna(False)
            df['delay_hours'] = ((df['actual_completion'] - df['expected_completion']).dt.total_seconds() / 3600).fillna(0)
            df['delay_hours'] = df['delay_hours'].clip(lower=0)
            
            # Calculate TAT
            df['tat_hours'] = ((df['actual_completion'] - df['submitted_at']).dt.total_seconds() / 3600).fillna(0)
            
            # SLA compliance
            df['sla_compliance'] = (~df['is_delayed']).astype(int)
            
            # Time features
            df['submission_day_of_week'] = df['submitted_at'].dt.dayofweek
            df['submission_month'] = df['submitted_at'].dt.month
            df['submission_year'] = df['submitted_at'].dt.year
            
            # Calculate historical delay rates
            if 'district' in df.columns:
                df['historical_delay_rate_district'] = df.groupby('district')['is_delayed'].transform('mean')
            if 'mandal' in df.columns:
                df['historical_delay_rate_mandal'] = df.groupby('mandal')['is_delayed'].transform('mean')
            if 'service_code' in df.columns:
                df['historical_delay_rate_service'] = df.groupby('service_code')['is_delayed'].transform('mean')
            
            logger.info(f"Processed {len(df)} historical records")
            return df
            
        except Exception as e:
            logger.error(f"Error processing historical data: {e}")
            raise
    
    def process_real_time_data(self, service_data: Dict) -> Dict:
        """Process real-time service data"""
        try:
            # Calculate current metrics
            metrics = calculate_delay_metrics(service_data)
            service_data.update(metrics)
            
            # Add processing timestamp
            service_data['processed_at'] = datetime.now().isoformat()
            
            return service_data
        except Exception as e:
            logger.error(f"Error processing real-time data: {e}")
            return service_data
    
    def aggregate_metrics(self, df: pd.DataFrame, group_by: List[str]) -> pd.DataFrame:
        """Aggregate metrics by specified columns"""
        try:
            agg_dict = {
                'is_delayed': ['sum', 'count', 'mean'],
                'delay_hours': ['mean', 'median', 'max'],
                'tat_hours': ['mean', 'median'],
                'sla_compliance': 'mean'
            }
            
            # Filter to only columns that exist
            agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
            
            aggregated = df.groupby(group_by).agg(agg_dict).reset_index()
            
            # Flatten column names
            aggregated.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in aggregated.columns.values]
            
            return aggregated
        except Exception as e:
            logger.error(f"Error aggregating metrics: {e}")
            return pd.DataFrame()
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to file"""
        try:
            filepath = self.processed_data_path / filename
            df.to_csv(filepath, index=False)
            logger.info(f"Saved processed data to {filepath}")
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
    
    def load_processed_data(self, filename: str) -> pd.DataFrame:
        """Load processed data from file"""
        try:
            filepath = self.processed_data_path / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                # Convert datetime columns
                datetime_cols = ['submitted_at', 'expected_completion', 'actual_completion', 'processed_at']
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                return df
            else:
                logger.warning(f"File {filepath} not found")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return pd.DataFrame()
    
    def batch_process_services(self, batch_size: int = 1000):
        """Process services in batches"""
        try:
            all_services = self.service_manager.get_all_services()
            total = len(all_services)
            
            logger.info(f"Processing {total} services in batches of {batch_size}")
            
            processed = []
            for i in range(0, total, batch_size):
                batch = all_services[i:i+batch_size]
                processed_batch = [self.process_real_time_data(s) for s in batch]
                processed.extend(processed_batch)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(total-1)//batch_size + 1}")
            
            # Update services in manager
            for service in processed:
                self.service_manager.update_service(
                    service.get('service_id'),
                    {k: v for k, v in service.items() if k not in ['service_id']}
                )
            
            logger.info(f"Batch processing completed: {len(processed)} services processed")
            return processed
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise

