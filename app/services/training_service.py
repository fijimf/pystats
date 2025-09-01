import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression

class TrainingService:
    def train_model(self, features, targets, key, as_of):
        """Train a machine learning model with provided data"""
        X = pd.DataFrame(features)
        y = pd.DataFrame(targets)
        
        print(f"Features shape: {X.shape}")
        print(f"Features columns: {X.columns}")
        print(f"Targets shape: {y.shape}")
        print(f"Targets columns: {y.columns}")
        
        pipeline = self._create_pipeline(key, as_of, X, y)
        pipeline.fit(X, y)
        score = pipeline.score(X, y)
        
        filename = f'{key}_{as_of}.pkl'
        joblib.dump(pipeline, filename)
        
        print(f"Model trained with score: {score}")
        
        return {
            'status': 'trained',
            'message': f"Score: {score}",
            'pipeline': filename
        }
    
    def _create_pipeline(self, key, as_of, X, y):
        """Create appropriate pipeline based on model key"""
        if key == 'basic-margin':
            return self._train_base_model(X, y, as_of)
        elif key == 'neural':
            return self._train_neural_model(X, y, as_of)
        else:
            raise ValueError(f"Unknown model type: {key}")
    
    def _train_base_model(self, X, y, as_of):
        """Create basic linear regression pipeline"""
        pipeline = Pipeline([
            ('onehot_home', OneHotEncoder(sparse_output=False, handle_unknown='ignore', categories='auto')),
            ('classifier', LinearRegression())
        ])
        return pipeline
    
    def _train_neural_model(self, X, y, as_of):
        """Placeholder for neural network model"""
        raise NotImplementedError("Neural network model not yet implemented")