import pandas as pd
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import lsqr
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def least_squares_power_estimator(df):
    """
    Calculate team power ratings using least squares estimation.
    
    Parameters:
    df : DataFrame containing game data with home_code, away_code, home_score, away_score
    
    Returns:
    pandas.Series : Team ratings sorted in descending order
    """
    teams = pd.unique(df[['home_code', 'away_code']].values.ravel())
    team_to_idx = {team: i for i, team in enumerate(teams)}
    n_teams = len(teams)
    n_games = len(df)
    
    X = lil_matrix((n_games, n_teams))
    
    for i, (t1, t2) in enumerate(zip(df['home_code'], df['away_code'])):
        X[i, team_to_idx[t1]] = 1   # +1 for home team
        X[i, team_to_idx[t2]] = -1  # -1 for away team

    X = X.tocsr()
    y = (df['home_score'] - df['away_score']).values
    ratings = lsqr(X, y)[0]
    team_ratings = pd.Series(ratings, index=teams).sort_values(ascending=False)
    
    return team_ratings

def logistic_power_estimator(df):
    """
    Calculate team power ratings using logistic regression.
    
    Parameters:
    df : DataFrame containing game data with home_code, away_code, home_score, away_score
    
    Returns:
    pandas.Series : Team ratings sorted in descending order
    """
    teams = pd.unique(df[['home_code', 'away_code']].values.ravel())
    team_to_idx = {team: i for i, team in enumerate(teams)}
    n_teams = len(teams)
    n_games = len(df)
    
    X = lil_matrix((n_games, n_teams))
    
    for i, (t1, t2) in enumerate(zip(df['home_code'], df['away_code'])):
        X[i, team_to_idx[t1]] = 1   # +1 for home team
        X[i, team_to_idx[t2]] = -1  # -1 for away team

    X = X.tocsr()
    y = (df['home_score'] > df['away_score']).astype(int).values
    
    # Split the data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Make predictions and evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Logistic regression accuracy: {accuracy:.2f}")
    
    # Get team ratings from model coefficients
    team_ratings = pd.Series(model.coef_[0], index=teams).sort_values(ascending=False)
    
    return team_ratings