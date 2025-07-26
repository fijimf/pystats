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

# Set up environment variables (DATABASE_URL required)
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Run development server
flask run

# Run in debug mode (via app.py directly)
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
- Tables are reflected at runtime using `db.Model.metadata.reflect(bind=db.engine)`

#### API Endpoints (`app.py`)
- `/api/health` - Health check endpoint
- `/api/games` - Retrieve season games data with optional filtering by year and team_id
- `/api/rankings/lse` - Least squares power rankings over time
- `/api/rankings/logistic` - Logistic regression power rankings over time  
- `/train` - POST endpoint for training ML models with custom pipelines

#### Statistical Analysis Functions
- `least_squares_power_esitimator()` - Uses sparse matrix operations (lil_matrix/lsqr) for team power ratings
- `logistic_power_esitimator()` - Logistic regression approach with train/test split
- `calc_by_dates()` - Processes rankings over date ranges for temporal analysis
- Both functions handle team-vs-team sparse matrices for efficient computation

#### Machine Learning Pipeline
- Supports multiple model types: 'basic-margin' (LinearRegression), 'neural' (placeholder)
- Uses scikit-learn Pipeline with OneHotEncoder preprocessing
- Models saved as joblib .pkl files with naming: `{key}_{asOf}.pkl`
- Training endpoint accepts JSON with features, targets, key, and asOf parameters

### Database Configuration
- Requires existing PostgreSQL database with sports data schema
- Uses DATABASE_URL environment variable for connection
- Core query joins: game ↔ season, game ↔ team (home/away), filtering by scores > 0
- Application designed for READ permissions on existing sports data

### CI/CD Pipeline (Jenkinsfile)
- Docker-based testing with PostgreSQL test database (postgres:15)
- Creates isolated test network for container communication
- Health check validation during deployment (curl /api/health)
- Automatic cleanup of test resources (containers, networks)
- Supports branch-based tagging (release branches get 'latest' tag)