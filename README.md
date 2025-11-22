# AI-Enabled Monitoring and Prediction of Service Delivery Delays

An AI-powered system to monitor and predict service delivery delays across 450+ GSWS citizen services, ensuring timely resolutions and improved accountability.

## Overview

This system provides:
- **AI-Powered SLA Prediction**: Predicts delays in Category-B services using historical data and real-time tracking
- **Root Cause Analysis**: Identifies workflow stages and administrative units where delays are frequent
- **Visualization and Alerts**: Dashboards for administrators to visualize SLA adherence trends and hotspots
- **API Integration**: RESTful APIs for seamless integration with existing departmental dashboards

## Project Structure

```
├── app/                    # Main application
│   ├── api/               # FastAPI endpoints
│   ├── models/            # ML models and training
│   ├── services/          # Business logic
│   ├── schemas/           # Data models
│   └── utils/             # Utility functions
├── dashboard/             # Streamlit dashboard
├── data/                  # Data storage and processing
│   ├── raw/              # Raw data
│   ├── processed/        # Processed data
│   └── models/           # Trained model artifacts
├── notebooks/            # Jupyter notebooks for analysis
├── tests/                # Unit tests
├── config/               # Configuration files
└── requirements.txt      # Python dependencies
```

## Features

### 1. SLA Prediction
- Time series forecasting for service completion times
- Classification models to predict delay probability
- Real-time prediction based on current workflow status

### 2. Root Cause Analysis
- Identify bottlenecks at workflow stages (VRO, Revenue Inspector, Tahsildar)
- District and mandal-level delay pattern analysis
- Service category trend analysis

### 3. Dashboard
- Real-time SLA monitoring
- Delay prediction alerts
- Heatmaps for delay hotspots
- Trend analysis and forecasting

### 4. API Endpoints
- `/api/v1/predict` - Get delay predictions
- `/api/v1/analytics` - Get analytics and insights
- `/api/v1/root-cause` - Root cause analysis
- `/api/v1/services` - Service management
- `/api/v1/dashboard` - Dashboard data

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AI-Prediction-Service-Delivery-Delays
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Start the API Server
```bash
uvicorn app.api.main:app --reload --port 8000
```

### Start the Dashboard
```bash
streamlit run dashboard/main.py
```

### Train Models
```bash
python app/models/train.py
```

## Configuration

Edit `config/config.yaml` to configure:
- Service categories and SLAs
- Model parameters
- API settings
- Database connections

## Data Format

The system expects data in the following format:
- Service requests with timestamps at each workflow stage
- District, mandal, and service category information
- Historical SLA compliance data

## API Documentation

Once the API server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This project is developed for the GSWS Department, Government of Andhra Pradesh.
