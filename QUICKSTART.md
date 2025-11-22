# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (if not already done):
```bash
cd AI-Prediction-Service-Delivery-Delays
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Running the System

### 1. Train the Models (Optional - for first-time setup)

The system will create dummy models automatically, but you can train models with sample data:

```bash
python app/train.py --samples 1000
```

### 2. Start the API Server

In one terminal window:

```bash
python run_api.py
```

Or using uvicorn directly:
```bash
uvicorn app.api.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000

- API Documentation (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

### 3. Start the Dashboard

In another terminal window:

```bash
python run_dashboard.py
```

Or using streamlit directly:
```bash
streamlit run dashboard/main.py
```

The dashboard will be available at: http://localhost:8501

## Using the API

### Example: Get Predictions

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_horizon_days": 7,
    "district": "Visakhapatnam"
  }'
```

### Example: Get Analytics

```bash
curl -X POST "http://localhost:8000/api/v1/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-01-31T23:59:59"
  }'
```

### Example: Create a Service Request

```bash
curl -X POST "http://localhost:8000/api/v1/services" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "SRV-2024-001234",
    "service_code": "CAT-B-001",
    "service_name": "Income Certificate",
    "category": "CATEGORY_B",
    "district": "Visakhapatnam",
    "mandal": "Visakhapatnam Urban",
    "submitted_at": "2024-01-15T10:00:00",
    "current_stage": "VRO",
    "status": "IN_PROGRESS",
    "sla_days": 7
  }'
```

## Dashboard Features

1. **Overview Tab**: 
   - Key metrics (Total Services, SLA Compliance, Delayed Services)
   - Risk predictions summary
   - Trend charts

2. **Predictions Tab**:
   - Delay predictions for all services
   - High-risk service alerts
   - Risk distribution charts

3. **Analytics Tab**:
   - District performance metrics
   - Service trends
   - SLA compliance by district

4. **Root Cause Analysis Tab**:
   - Primary delay causes
   - Stage bottlenecks
   - Actionable recommendations

## Configuration

Edit `config/config.yaml` to customize:
- Service categories and SLAs
- Model parameters
- API settings
- Workflow stages

## Data Management

### Initialize Sample Data

The API automatically initializes with 100 sample services on first startup. To generate more:

```python
from app.services.service_manager import ServiceManager

manager = ServiceManager()
manager.initialize_sample_data(1000)
```

### Process Data

```python
from app.data_processor import DataProcessor
from app.services.service_manager import ServiceManager

manager = ServiceManager()
processor = DataProcessor(manager)
processor.batch_process_services()
```

## Troubleshooting

### Port Already in Use

If port 8000 or 8501 is already in use, change the port in:
- API: Edit `run_api.py` or use `--port` flag with uvicorn
- Dashboard: Edit `run_dashboard.py` or use `--server.port` flag with streamlit

### Missing Dependencies

If you encounter import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Model Not Found

The system will automatically create dummy models if trained models are not found. To train models:
```bash
python app/train.py
```

## Next Steps

1. **Integrate with Real Data**: Replace sample data with actual service data from AP Seva, MeeSeva, and Mana Mitra platforms
2. **Customize Models**: Adjust model parameters in `config/config.yaml` based on your data
3. **Add Alerts**: Implement notification channels (email, SMS) for high-risk predictions
4. **Scale Up**: Deploy to production with proper database (PostgreSQL, MySQL) instead of JSON files

## Support

For issues or questions, please refer to the main README.md or contact the development team.

