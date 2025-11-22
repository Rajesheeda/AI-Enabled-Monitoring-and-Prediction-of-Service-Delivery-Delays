"""
Service Manager
Manages service requests and data storage
"""
from typing import List, Dict, Optional
from datetime import datetime
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manages service request data"""
    
    def __init__(self, data_path: str = "./data/services.json"):
        self.data_path = data_path
        Path(os.path.dirname(data_path)).mkdir(parents=True, exist_ok=True)
        self._services = []
        self._load_services()
    
    def _load_services(self):
        """Load services from storage"""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r') as f:
                    self._services = json.load(f)
            else:
                self._services = []
                self._save_services()
        except Exception as e:
            logger.error(f"Error loading services: {e}")
            self._services = []
    
    def _save_services(self):
        """Save services to storage"""
        try:
            with open(self.data_path, 'w') as f:
                json.dump(self._services, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving services: {e}")
    
    def add_service(self, service_data: Dict) -> Dict:
        """Add a new service request"""
        try:
            service_data['created_at'] = datetime.now().isoformat()
            self._services.append(service_data)
            self._save_services()
            return service_data
        except Exception as e:
            logger.error(f"Error adding service: {e}")
            raise
    
    def get_service(self, service_id: str) -> Optional[Dict]:
        """Get a service by ID"""
        for service in self._services:
            if service.get('service_id') == service_id:
                return service
        return None
    
    def update_service(self, service_id: str, updates: Dict) -> Optional[Dict]:
        """Update a service"""
        for i, service in enumerate(self._services):
            if service.get('service_id') == service_id:
                self._services[i].update(updates)
                self._services[i]['updated_at'] = datetime.now().isoformat()
                self._save_services()
                return self._services[i]
        return None
    
    def list_services(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List all services with optional filters"""
        services = self._services.copy()
        
        if filters:
            if filters.get('district'):
                services = [s for s in services if s.get('district') == filters['district']]
            if filters.get('mandal'):
                services = [s for s in services if s.get('mandal') == filters['mandal']]
            if filters.get('service_code'):
                services = [s for s in services if s.get('service_code') == filters['service_code']]
            if filters.get('category'):
                services = [s for s in services if s.get('category') == filters['category']]
            if filters.get('status'):
                services = [s for s in services if s.get('status') == filters['status']]
        
        return services
    
    def get_all_services(self) -> List[Dict]:
        """Get all services"""
        return self._services.copy()
    
    def initialize_sample_data(self, n_samples: int = 100):
        """Initialize with sample data for demonstration"""
        from app.models.trainer import ModelTrainer
        
        trainer = ModelTrainer()
        df = trainer.generate_sample_data(n_samples)
        
        self._services = df.to_dict('records')
        self._save_services()
        logger.info(f"Initialized {len(self._services)} sample services")

