# System Architecture

## Overview

The GSWS SLA Monitoring System is built using a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                      │
│              (Visualization & User Interface)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                         │
│  (Predictions, Analytics, Services, Dashboard Endpoints)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Prediction  │ │  Analytics   │ │   Service    │
│   Service    │ │   Service    │ │   Manager    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────┬───┴────────────────┘
                    ▼
         ┌──────────────────────┐
         │   ML Models Layer    │
         │  (Delay Predictor)   │
         └──────────┬───────────┘
                    │
         ┌──────────┴───────────┐
         ▼                      ▼
┌──────────────┐      ┌──────────────┐
│   Data       │      │   Model      │
│  Processor   │      │   Trainer    │
└──────────────┘      └──────────────┘
```

## Components

### 1. API Layer (`app/api/`)

**FastAPI Application** providing RESTful endpoints:
- `/api/v1/predict` - Delay predictions
- `/api/v1/analytics` - Analytics and insights
- `/api/v1/root-cause` - Root cause analysis
- `/api/v1/services` - Service management
- `/api/v1/dashboard/*` - Dashboard data endpoints

### 2. Service Layer (`app/services/`)

Business logic layer:
- **PredictionService**: Handles delay prediction requests
- **AnalyticsService**: Performs root cause analysis and analytics
- **ServiceManager**: Manages service request data (CRUD operations)

### 3. Model Layer (`app/models/`)

Machine Learning components:
- **DelayPredictor**: Predicts delays using trained ML models (XGBoost/LightGBM)
- **ModelTrainer**: Trains models on historical data

### 4. Data Layer (`app/schemas/`, `app/data_processor.py`)

- **Schemas**: Pydantic models for data validation
- **DataProcessor**: Processes historical and real-time data

### 5. Dashboard (`dashboard/`)

Streamlit-based visualization dashboard with:
- Overview metrics
- Prediction visualization
- Analytics charts
- Root cause analysis

## Data Flow

### Prediction Flow

1. User requests prediction via API
2. ServiceManager retrieves service data
3. PredictionService filters services based on request
4. DelayPredictor generates predictions for each service
5. Results aggregated and returned

### Analytics Flow

1. User requests analytics via API
2. ServiceManager retrieves historical service data
3. AnalyticsService filters and processes data
4. Root cause analysis performed
5. Metrics calculated and returned

### Training Flow

1. Historical data loaded/generated
2. Features extracted and prepared
3. Models trained (classifier + regressor)
4. Models evaluated and saved
5. Models loaded for predictions

## Technology Stack

- **Backend Framework**: FastAPI
- **ML Libraries**: XGBoost, LightGBM, scikit-learn
- **Data Processing**: Pandas, NumPy
- **Dashboard**: Streamlit, Plotly
- **Data Validation**: Pydantic
- **Configuration**: YAML

## Data Storage

Currently uses JSON files for simplicity. Production deployment should use:
- **PostgreSQL/MySQL** for service data
- **Redis** for caching
- **Object Storage** (S3/MinIO) for model artifacts

## Model Architecture

### Delay Classification Model
- **Type**: Binary Classifier (XGBoost/Random Forest)
- **Input**: Service features (stage, district, historical rates, etc.)
- **Output**: Delay probability (0-1)

### Delay Regression Model
- **Type**: Regressor (XGBoost/Random Forest)
- **Input**: Same as classifier
- **Output**: Predicted delay hours

### Features Used
- Days since submission
- Current workflow stage
- District and mandal
- Service code and category
- Historical delay rates
- Workload at stage
- Time features (day of week, month, weekend)

## API Design

RESTful API following OpenAPI specification:
- Standard HTTP methods (GET, POST, PUT)
- JSON request/response format
- Comprehensive error handling
- Swagger/ReDoc documentation

## Security Considerations

For production deployment, add:
- Authentication (JWT tokens)
- Authorization (role-based access)
- Rate limiting
- Input validation and sanitization
- HTTPS/TLS encryption
- API key management

## Scalability

The system is designed to scale:
- Stateless API design (horizontal scaling)
- Model caching for performance
- Batch processing capabilities
- Async operations where applicable

## Monitoring

Recommended monitoring:
- API response times
- Model prediction accuracy
- Error rates
- System resource usage
- Data processing throughput

