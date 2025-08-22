from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from scipy import stats
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import lsqr
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
print(app.config['SQLALCHEMY_DATABASE_URI'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-RESTX with API documentation
api = Api(app, 
    title='PyStats API',
    version='1.0',
    description='Statistical analysis API for sports data with machine learning capabilities',
    doc='/swagger/',
    prefix='/api'
)

# Import and create models after db initialization to avoid circular imports
from models import create_models

# Reflect the database tables
with app.app_context():
    db.Model.metadata.reflect(bind=db.engine)
    # Create the models
    TeamStatistic = create_models(db)

# Define API models for documentation
health_model = api.model('Health', {
    'status': fields.String(description='API health status'),
    'message': fields.String(description='Health check message')
})

error_model = api.model('Error', {
    'status': fields.String(description='Error status'),
    'message': fields.String(description='Error message')
})

rankings_response_model = api.model('RankingsResponse', {
    'status': fields.String(description='Response status'),
    'data': fields.Raw(description='Team rankings data by date')
})

training_request_model = api.model('TrainingRequest', {
    'features': fields.Raw(required=True, description='Feature data for training'),
    'targets': fields.Raw(required=True, description='Target data for training'),
    'key': fields.String(required=True, description='Model type key (basic-margin, neural)'),
    'asOf': fields.String(required=True, description='Training date/version identifier')
})

training_response_model = api.model('TrainingResponse', {
    'status': fields.String(description='Training status'),
    'message': fields.String(description='Training result message'),
    'pipeline': fields.String(description='Saved pipeline filename')
})


@api.route('/health')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.marshal_with(health_model)
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'message': 'PyStats API is running'
        }


@api.route('/rankings/lse')
class LSERankings(Resource):
    @api.doc('get_lse_rankings')
    @api.marshal_with(rankings_response_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get least squares power rankings over time
        
        Returns team power rankings calculated using least squares estimation,
        computed for each date in the current season.
        """
        try:
            team_ratings_list = calc_by_dates(least_squares_power_esitimator)       
            return {
                'status': 'success',
                'data': team_ratings_list
            }
        except Exception as e:
            api.abort(500, status='error', message=str(e))

@api.route('/rankings/logistic')
class LogisticRankings(Resource):
    @api.doc('get_logistic_rankings')
    @api.marshal_with(rankings_response_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get logistic regression power rankings over time
        
        Returns team power rankings calculated using logistic regression,
        computed for each date in the current season.
        """
        try:
            team_ratings_list = calc_by_dates(logistic_power_esitimator)       
            return {
                'status': 'success',
                'data': team_ratings_list
            }
        except Exception as e:
            api.abort(500, status='error', message=str(e))

@api.route('/train')
class ModelTraining(Resource):
    @api.doc('train_model')
    @api.expect(training_request_model)
    @api.marshal_with(training_response_model)
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Train a machine learning model with provided data
        
        Accepts training features and targets to create and save a ML pipeline.
        Supports different model types specified by the 'key' parameter.
        """
        payload = api.payload
        X = pd.DataFrame(payload['features'])
        print(X)
        print(X.columns)
        print(X.dtypes)
        print(X.head()) 
        print(X.info())
        y = pd.DataFrame(payload['targets'])
        print(y)
        print(y.columns)
        print(y.dtypes)
        print(y.head())
        print(y.info())

        key = payload['key']
        asOf = payload['asOf']

        return createPipeline(key, asOf, X, y)

def createPipeline(key, asOf, X, y):
    try:
      # Dispatch to different training functions based on the key
        if key == 'basic-margin':
            pipeline =train_base_model(X, y, asOf)
        elif key == 'neural':
            pipeline = train_neural_model(X, y, asOf)
        else:
            raise ValueError(f"Unknown model type: {key}")

        # Create a pipeline with preprocessing and model
        pipeline.fit(X, y)
        score = pipeline.score(X, y)
        print(f"Score: {score}")
        joblib.dump(pipeline, key+'_'+asOf+'.pkl') 
        return {
            'status': 'trained',
            'message': f"Score: {score}",
            'pipeline': key+'_'+asOf+'.pkl'
        }
    except Exception as e:
        api.abort(500, status='error', message=str(e))


def train_base_model(X, y, asOf):
    pipeline = Pipeline([
        ('onehot_home', OneHotEncoder(sparse_output=False, handle_unknown='ignore', categories='auto')),
        ('classifier', LinearRegression())]
    )
    return pipeline

    
def _load_games_by_season(year=None, team_id=None):
    if year is None:
        year = request.args.get('year')
    if team_id is None:
        team_id = request.args.get('team_id')
    
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    base_query = """SELECT s.year, g.date, h.long_name home_team, h.abbreviation home_code, g.home_score, 
                           a.long_name away_team, a.abbreviation away_code, g.away_score, g.neutral_site 
                    FROM game g
                    INNER JOIN season s ON g.season_id = s.id
                    INNER JOIN team h ON g.home_team_id = h.id
                    INNER JOIN team a ON g.away_team_id = a.id
                    WHERE g.home_score>0 and g.away_score>0"""
    
    conditions = []
    if year:
        conditions.append(f"s.year = {year}")
    if team_id:
        conditions.append(f"(h.id = {team_id} OR a.id = {team_id})")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY date, h.long_name, a.long_name"
    
    df = pd.read_sql(base_query, engine)
    return df

def calc_by_dates(processor_func):
    df = _load_games_by_season()
    min_date = df['date'].min()
    max_date = df['date'].max()
    dates = pd.date_range(start=min_date, end=max_date, freq='D')

    team_ratings_list = {}
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        # Convert date_str to datetime for comparison
        df_subset = df[pd.to_datetime(df['date']) <= pd.to_datetime(date_str)]
        if len(df_subset) == 0:
            continue
        team_ratings = processor_func(df_subset)
        team_ratings_list[date_str] = team_ratings.to_dict()
    return team_ratings_list

def least_squares_power_esitimator(df):
    teams = pd.unique(df[['home_code', 'away_code']].values.ravel())
    team_to_idx = {team: i for i, team in enumerate(teams)}
    n_teams = len(teams)
    n_games = len(df)
    X = lil_matrix((n_games, n_teams))  # Use LIL format for efficient row operations

    for i, (t1, t2) in enumerate(zip(df['home_code'], df['away_code'])):
        X[i, team_to_idx[t1]] = 1  # +1 for team1
        X[i, team_to_idx[t2]] = -1  # -1 for team2

    X = X.tocsr()
    y = (df['home_score'] - df['away_score']).values
    ratings = lsqr(X, y)[0]  # Solve the sparse least squares problem
    team_ratings = pd.Series(ratings, index=teams).sort_values(ascending=False)
    return team_ratings

def logistic_power_esitimator(df):
    teams = pd.unique(df[['home_code', 'away_code']].values.ravel())
    team_to_idx = {team: i for i, team in enumerate(teams)}
    n_teams = len(teams)
    n_games = len(df)
    X = lil_matrix((n_games, n_teams))  # Use LIL format for efficient row operations

    for i, (t1, t2) in enumerate(zip(df['home_code'], df['away_code'])):
        X[i, team_to_idx[t1]] = 1  # +1 for team1
        X[i, team_to_idx[t2]] = -1  # -1 for team2

    X = X.tocsr()
    y = (df['home_score'] > df['away_score']).astype(int).values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")
    
    # Get team ratings from model coefficients
    team_ratings = pd.Series(model.coef_[0], index=teams).sort_values(ascending=False)
    return team_ratings

if __name__ == '__main__':
    print("Starting PyStats API...")
    print("Database URL: ", os.getenv('DATABASE_URL'))
    app.run(debug=True) 