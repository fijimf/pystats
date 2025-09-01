import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline


class TeamOneHotEncoder(BaseEstimator, TransformerMixin):
    """
    Custom transformer that creates one-hot encoding where:
    - Home team gets +1 in its column
    - Away team gets -1 in its column
    """
    
    def __init__(self):
        self.teams_ = None
        self.team_to_index_ = None
    
    def fit(self, X, y=None):
        """
        Learn the unique teams from both homeTeam and awayTeam columns.
        
        Parameters:
        X : DataFrame with 'homeTeam' and 'awayTeam' columns
        y : Ignored
        
        Returns:
        self
        """
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        if 'homeTeam' not in X.columns or 'awayTeam' not in X.columns:
            raise ValueError("DataFrame must contain 'homeTeam' and 'awayTeam' columns")
        
        # Get all unique teams from both columns
        all_teams = set(X['homeTeam'].unique()) | set(X['awayTeam'].unique())
        self.teams_ = sorted(list(all_teams))
        self.team_to_index_ = {team: idx for idx, team in enumerate(self.teams_)}
        
        return self
    
    def transform(self, X):
        """
        Transform the DataFrame into the encoded matrix.
        
        Parameters:
        X : DataFrame with 'homeTeam' and 'awayTeam' columns
        
        Returns:
        numpy array of shape (n_samples, n_teams)
        """
        if self.teams_ is None:
            raise ValueError("Transformer has not been fitted yet")
        
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        if 'homeTeam' not in X.columns or 'awayTeam' not in X.columns:
            raise ValueError("DataFrame must contain 'homeTeam' and 'awayTeam' columns")
        
        n_samples = len(X)
        n_teams = len(self.teams_)
        
        # Initialize the encoding matrix
        encoded = np.zeros((n_samples, n_teams))
        
        # Encode home teams as +1
        for idx, home_team in enumerate(X['homeTeam']):
            if home_team in self.team_to_index_:
                team_idx = self.team_to_index_[home_team]
                encoded[idx, team_idx] = 1
        
        # Encode away teams as -1
        for idx, away_team in enumerate(X['awayTeam']):
            if away_team in self.team_to_index_:
                team_idx = self.team_to_index_[away_team]
                encoded[idx, team_idx] = -1
        
        return encoded
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names for the encoded output."""
        if self.teams_ is None:
            raise ValueError("Transformer has not been fitted yet")
        return np.array([f"team_{team}" for team in self.teams_])


def create_margin_pipeline():
    """
    Create a sklearn pipeline for margin prediction using team encoding.
    
    Returns:
    sklearn.pipeline.Pipeline
    """
    return Pipeline([
        ('encoder', TeamOneHotEncoder()),
        ('regressor', LinearRegression())
    ])


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'homeTeam': ['TeamA', 'TeamB', 'TeamC', 'TeamA'],
        'awayTeam': ['TeamB', 'TeamC', 'TeamA', 'TeamC']
    })
    
    # Sample target values (e.g., point margins)
    sample_target = np.array([5, -3, 8, 2])
    
    # Create and fit the pipeline
    pipeline = create_margin_pipeline()
    pipeline.fit(sample_data, sample_target)
    
    # Make predictions
    predictions = pipeline.predict(sample_data)
    print("Predictions:", predictions)
    
    # Get feature names
    feature_names = pipeline.named_steps['encoder'].get_feature_names_out()
    print("Feature names:", feature_names)
    
    # Get coefficients
    coefficients = pipeline.named_steps['regressor'].coef_
    print("Team coefficients:", dict(zip(feature_names, coefficients)))

    pipeline.score