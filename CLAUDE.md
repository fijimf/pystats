# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Local Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
flask run

# Run in debug mode (via app.py)
python app.py
```

### Docker Development
```bash
# Build Docker image
docker build -t pystats:latest .

# Run with Docker (requires DATABASE_URL environment variable)
docker run -e DATABASE_URL=postgresql://user:pass@host:5432/db -p 8000:8000 pystats:latest
```

### Production Deployment
- Uses Gunicorn WSGI server on port 8000
- Configured in Dockerfile: `gunicorn --bind 0.0.0.0:8000 --workers 4 app:app`
- Requires PostgreSQL database connection via DATABASE_URL environment variable

## Architecture Overview

### Core Application Structure
- **Flask REST API** for statistical analysis of sports data
- **PostgreSQL database** with existing schema (uses SQLAlchemy reflection)
- **Statistical computing** with pandas, numpy, scipy, and scikit-learn
- **Machine learning pipelines** for predictive modeling

### Key Components

#### Database Layer (`models.py`)
- Uses SQLAlchemy reflection to map existing database tables
- Primary model: `TeamStatistic` with fields: id, team_id, stat_type, value, timestamp
- Database schema includes: game, season, team tables with relationships

#### API Endpoints (`app.py`)
- `/api/health` - Health check endpoint
- `/api/games` - Retrieve season games data with optional filtering
- `/api/rankings/lse` - Least squares power rankings over time
- `/api/rankings/logistic` - Logistic regression power rankings over time  
- `/train` - POST endpoint for training ML models with custom pipelines

#### Statistical Analysis Functions
- `least_squares_power_estimator()` - Uses sparse matrix operations for team power ratings
- `logistic_power_estimator()` - Logistic regression approach with train/test split
- `calc_by_dates()` - Processes rankings over date ranges for temporal analysis

#### Machine Learning Pipeline
- Supports multiple model types: 'basic-margin' (LinearRegression), 'neural' (placeholder)
- Uses scikit-learn Pipeline with OneHotEncoder preprocessing
- Models saved as joblib .pkl files with naming: `{key}_{asOf}.pkl`

### Database Configuration
- Requires existing PostgreSQL database with sports data schema
- Uses DATABASE_URL environment variable for connection
- Tables: game, season, team, team_statistic with foreign key relationships
- Application connects with READ permissions to existing data

### CI/CD Pipeline (Jenkinsfile)
- Docker-based testing with PostgreSQL test database
- Health check validation during deployment
- Network isolation for containerized testing
- Automatic cleanup of test resources