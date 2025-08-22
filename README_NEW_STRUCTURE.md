# PyStats API - Refactored Structure

## Overview
The PyStats API has been refactored to follow a more scalable, maintainable architecture with proper separation of concerns.

## Key Improvements

### 1. Modular Architecture
- **Application Factory Pattern**: Uses Flask application factory for better testability
- **Blueprint-like Structure**: API routes are organized in separate modules
- **Service Layer**: Business logic separated from API controllers
- **Configuration Management**: Environment-based configurations

### 2. Directory Structure
```
pystats/
├── app/                    # Main application package
│   ├── api/               # API route handlers
│   ├── config/            # Configuration management
│   ├── models/            # Database models
│   ├── services/          # Business logic layer
│   ├── statistical/       # Statistical analysis functions
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── run.py                 # Application entry point
└── requirements.txt       # Dependencies
```

### 3. Benefits
- **Scalability**: Easy to add new features and endpoints
- **Maintainability**: Clear separation of concerns
- **Testability**: Better unit testing capabilities
- **Configuration**: Environment-based settings
- **Error Handling**: Centralized error management
- **Logging**: Proper logging infrastructure

## Migration Guide

### Old vs New
- **OLD**: `python app.py` 
- **NEW**: `python run.py`

- **OLD**: Everything in single `app.py` file
- **NEW**: Modular structure with separate concerns

### API Endpoints (unchanged)
- `GET /api/health` - Health check
- `GET /api/rankings/lse` - Least squares rankings
- `GET /api/rankings/logistic` - Logistic regression rankings  
- `POST /api/train` - Train ML models
- `GET /swagger/` - API documentation

## Development
```bash
# Setup (same as before)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run application (new way)
export DATABASE_URL=postgresql://user:pass@host:5432/db
python run.py

# Run tests
python -m pytest tests/
```

## Docker
The Dockerfile should be updated to use `run.py` as the entry point:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "run:app"]
```

## Notes
- All original functionality is preserved
- Swagger/OpenAPI documentation still available at `/swagger/`
- Database configuration unchanged
- Environment variables work the same way