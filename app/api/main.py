"""
FastAPI Main Application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import yaml
from pathlib import Path

from app.api.routes import predictions, analytics, services, dashboard
from app.services.service_manager import ServiceManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config_path = Path("config/config.yaml")
if config_path.exists():
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
else:
    config = {}

# Initialize FastAPI app
app = FastAPI(
    title="GSWS SLA Monitoring System API",
    description="AI-powered system to monitor and predict service delivery delays",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service manager
service_manager = ServiceManager()

# Dependency to get service manager
def get_service_manager():
    return service_manager

# Include routers
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(services.router, prefix="/api/v1", tags=["Services"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GSWS SLA Monitoring System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "GSWS SLA Monitoring System"}

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting GSWS SLA Monitoring System API")
    # Initialize sample data if needed
    if len(service_manager.get_all_services()) == 0:
        logger.info("No services found, initializing sample data...")
        service_manager.initialize_sample_data(100)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

