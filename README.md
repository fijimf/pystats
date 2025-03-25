# PyStats API

A Flask-based REST API for advanced statistical analysis using PostgreSQL, pandas, numpy, and scipy.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and connection details to the existing database
```

4. Run the application:
```bash
flask run
```

## Database Configuration

This application is designed to work with an existing PostgreSQL database. Make sure to:
1. Update the `DATABASE_URL` in your `.env` file to point to your existing database
2. Ensure your database user has appropriate READ permissions on the required tables

## API Endpoints

### Health Check
- GET `/api/health`
  - Returns the API status

### Team Statistics
- GET `/api/team/stats`
  - Returns statistical analysis of team data
  - Query Parameters:
    - `team_id` (optional): Filter by specific team
    - `stat_type` (optional): Filter by specific statistic type
  - Returns:
    - mean
    - median
    - standard deviation
    - skewness
    - kurtosis
    - count
    - minimum value
    - maximum value

## Database Schema

The application uses SQLAlchemy's reflection capability to map to your existing database schema.

### Table Structure
- team_statistic
  - id: Primary key
  - team_id: Team identifier
  - stat_type: Type of statistic
  - value: Numerical value
  - timestamp: Time of record creation 