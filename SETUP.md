# Quick Setup Guide 🚀

## Prerequisites
- Python 3.10+
- Docker (optional)
- Git

## Local Setup

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd air-quality-mlops
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Data & Train Models
```bash
# Generate dataset
cd data
python generate_data.py
cd ..

# Run Prefect pipeline (trains all models)
cd src
python prefect_pipeline.py
cd ..
```

### 5. Start API Server
```bash
uvicorn src.api:app --reload
```

Visit: http://localhost:8000/docs

## Docker Setup

### Quick Start (Recommended)
```bash
# Build and run all services
docker-compose up --build

# API will be available at http://localhost:8000
# Prefect UI at http://localhost:4200
```

### Manual Docker Build
```bash
# Build image
docker build -t air-quality-api .

# Run container
docker run -p 8000:8000 air-quality-api

# Test health endpoint
curl http://localhost:8000/health
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suites
```bash
# Data quality tests
pytest tests/test_data_quality.py -v

# Model tests
pytest tests/test_models.py -v

# API tests
pytest tests/test_api.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## Project Workflow

1. **Data Preparation**
   ```bash
   cd data && python generate_data.py
   ```

2. **Run ML Pipeline**
   ```bash
   cd src && python prefect_pipeline.py
   ```

3. **Start API**
   ```bash
   uvicorn src.api:app --reload
   ```

4. **Make Predictions**
   - Visit http://localhost:8000/docs
   - Try the `/predict/aqi` or `/predict/pm25` endpoints

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Predict AQI Category
```bash
curl -X POST "http://localhost:8000/predict/aqi" \
  -H "Content-Type: application/json" \
  -d '{
    "PM2_5": 55.3,
    "PM10": 102.5,
    "NO2": 45.2,
    "SO2": 12.8,
    "CO": 85.3,
    "O3": 65.4,
    "temperature": 25.5,
    "humidity": 65.0,
    "wind_speed": 3.2,
    "hour": 14,
    "day_of_week": 2,
    "month": 6
  }'
```

### Predict PM2.5
```bash
curl -X POST "http://localhost:8000/predict/pm25" \
  -H "Content-Type: application/json" \
  -d '{
    "NO2": 45.2,
    "SO2": 12.8,
    "CO": 85.3,
    "O3": 65.4,
    "temperature": 25.5,
    "humidity": 65.0,
    "wind_speed": 3.2,
    "hour": 14,
    "day_of_week": 2,
    "month": 6
  }'
```

## CI/CD Pipeline

The project includes GitHub Actions workflow that:
1. ✅ Checks code quality (black, flake8, isort)
2. ✅ Validates data quality
3. ✅ Trains and tests models
4. ✅ Tests API endpoints
5. ✅ Builds Docker image
6. ✅ Deploys to production (on main branch)

## Troubleshooting

### Models Not Found
```bash
# Train models first
cd src && python prefect_pipeline.py
```

### Port Already in Use
```bash
# Use different port
uvicorn src.api:app --port 8001
```

### Docker Issues
```bash
# Clean up
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose up --build
```

## Next Steps

1. ✅ Review trained models in `models/` directory
2. ✅ Check pipeline report: `pipeline_report.txt`
3. ✅ Explore API documentation at `/docs`
4. ✅ Run tests to verify everything works
5. ✅ Push to GitHub to trigger CI/CD pipeline

## Support

For issues or questions:
- Check the main README.md
- Review logs in `logs/` directory
- Check GitHub Actions for CI/CD status
