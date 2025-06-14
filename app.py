from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models after db initialization to avoid circular imports
from models import *

# Reflect the database tables
with app.app_context():
    db.Model.metadata.reflect(bind=db.engine)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'PyStats API is running'
    })

@app.route('/api/games', methods=['GET'])
def get_season_games():
    """Get statistical analysis of team data"""
    try:
        year = request.args.get('year')
        engine = create_engine(os.getenv('DATABASE_URL'))
        df = pd.read_sql("""SELECT s.year, g.date, h.long_name home_team, h.abbreviation home_code, g.home_score, a.long_name away_team, a.abbreviation away_code, g.away_score, g.neutral_site FROM game g
                INNER JOIN season s ON g.season_id = s.id
                INNER JOIN team h ON g.home_team_id = h.id
                INNER JOIN team a ON g.away_team_id = a.id
                WHERE s.year = {} and g.home_score>0 and g.away_score>0
                ORDER BY date, h.long_name, a.long_name""".format(year), engine)
        # Get team_id from query parameters
        team_id = request.args.get('team_id')
        if team_id != None:
            df = df[(df['home_code'] == team_id) | (df['away_code'] == team_id)]
        
        return jsonify({
            'status': 'success',
            'data': df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/rankings/lse', methods=['GET'])
def get_rankings_lse():
    """Get statistical analysis of team data"""
    try:
        team_ratings_list = calc_by_dates(least_squares_power_esitimator)       
        return jsonify({
            'status': 'success',
            'data': team_ratings_list
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
            }), 500

@app.route('/api/rankings/logistic', methods=['GET'])
def get_rankings_logistic():
    try:
        team_ratings_list = calc_by_dates(logistic_power_esitimator)       
        return jsonify({
            'status': 'success',
            'data': team_ratings_list
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
            }), 500

@app.route('/train', methods=['POST'])
def train():
   
    payload = request.get_json()
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

    createPipeline(key, asOf, X, y)
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
        return jsonify({
            'status': 'trained',
            'message': f"Score: {score}",
            'pipeline': key+'_'+asOf+'.pkl'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def train_base_model(X, y, asOf):
    pipeline = Pipeline([
        ('onehot_home', OneHotEncoder(sparse_output=False, handle_unknown='ignore', categories='auto')),
        ('classifier', LinearRegression())]
    )
    return pipeline

    
def load_games_by_season():
    year = request.args.get('year')
    engine = create_engine(os.getenv('DATABASE_URL'))
    df = pd.read_sql("""SELECT s.year, g.date, h.long_name home_team, h.abbreviation home_code, g.home_score, a.long_name away_team, a.abbreviation away_code, g.away_score, g.neutral_site FROM game g
                INNER JOIN season s ON g.season_id = s.id
                INNER JOIN team h ON g.home_team_id = h.id
                INNER JOIN team a ON g.away_team_id = a.id
                WHERE s.year = {} and g.home_score>0 and g.away_score>0
                ORDER BY date, h.long_name, a.long_name""".format(year), engine)
    return df

def calc_by_dates(processor_func):
    df = load_games_by_season()
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
    app.run(debug=True) 