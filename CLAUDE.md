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
python run.py

# Or using Flask command
export FLASK_APP=run.py && flask run
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
- **Modular Flask REST API** for statistical analysis of sports data
- **PostgreSQL database** with existing schema (uses SQLAlchemy reflection)
- **Statistical computing** with pandas, numpy, scipy, and scikit-learn
- **Machine learning pipelines** for predictive modeling
- **Organized codebase** with separation of concerns and proper dependency injection

### Key Components

#### Project Structure
```
app/
├── __init__.py           # Application factory
├── api/                  # API route modules
│   ├── health.py        # Health check endpoints
│   ├── rankings.py      # Rankings API endpoints
│   └── training.py      # ML training endpoints
├── config/               # Configuration management
│   └── settings.py      # Environment-based configs
├── models/               # Database models
│   └── team_statistic.py # Database model definitions
├── services/             # Business logic layer
│   ├── data_service.py  # Database operations
│   ├── ranking_service.py # Rankings calculations
│   └── training_service.py # ML model training
├── statistical/          # Statistical analysis modules
│   ├── power_estimators.py # Team power rating algorithms
│   └── margin_linear_regressor.py # Custom ML transformers
└── utils/                # Utility functions
    ├── errors.py        # Custom exceptions
    └── logging.py       # Logging configuration
```

#### Database Layer (`app/models/`)
- Uses SQLAlchemy reflection to map existing database tables
- Primary model: `TeamStatistic` with fields: id, team_id, stat_type, value, timestamp
- Database schema includes: game, season, team tables with relationships
- Tables are reflected at runtime using `db.Model.metadata.reflect(bind=db.engine)`

#### API Layer (`app/api/`)
- `/api/health` - Health check endpoint
- `/api/rankings/lse` - Least squares power rankings over time
- `/api/rankings/logistic` - Logistic regression power rankings over time  
- `/api/train` - POST endpoint for training ML models with custom pipelines

#### Service Layer (`app/services/`)
- **DataService**: Database operations and data loading
- **RankingService**: Statistical analysis and team ranking calculations
- **TrainingService**: Machine learning model training and management

#### Statistical Analysis (`app/statistical/`)
- `least_squares_power_estimator()` - Uses sparse matrix operations (lil_matrix/lsqr) for team power ratings
- `logistic_power_estimator()` - Logistic regression approach with train/test split
- Custom ML transformers for sports data processing

#### Configuration Management (`app/config/`)
- Environment-based configuration (development, production, testing)
- Centralized settings management with proper defaults
- Support for different database configurations per environment

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