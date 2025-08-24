from typing import Dict, List, Any
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

from app.statistical.margin_linear_regressor import TeamOneHotEncoder
from app.statistical.model_interface import ModelInterface


class SampleLinearModel(ModelInterface):
    """Simple linear regression model for testing ML pipeline"""
    
    @property
    def name(self) -> str:
        return "naive-linear-regression"
    
    @property
    def type(self) -> str:
        return "SingleSeason"
    
    @property
    def description(self) -> str:
        return "Naive linear regression of scores using a one-hot encoding of the home and away teams"
    
    @property
    def feature_names(self) -> List[str]:
        return ["homeTeam", "awayTeam"]
    
    @property
    def label_names(self) -> List[str]:
        return ["margin"]

    def create_pipeline(self, parameters: Dict[str, Any]) -> Pipeline:
        """
        Create sklearn Pipeline with linear regression.
        Args:
            parameters: Dictionary of model-specific parameters
        Returns:
            Configured sklearn Pipeline ready for training
        """

        # Get parameters with defaults
        fit_intercept = parameters.get('fit_intercept', True)
        
        # Create pipeline steps
        steps = []
        
        steps.append(('encoder', TeamOneHotEncoder()))
        steps.append(('regressor', LinearRegression(fit_intercept=fit_intercept)))

        return Pipeline(steps)
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """
        Return default parameter values for the model.
        
        Returns:
            Dictionary of default parameters
        """
        return {
            'fit_intercept': True
        }
    
    def extract_metrics(self, pipeline: Pipeline, features: Any, labels: Any) -> Dict[str, float]:
        """
        Extract training metrics from fitted pipeline.
        
        Args:
            pipeline: Trained sklearn Pipeline
            features: Training features used
            labels: Training labels used
            
        Returns:
            Dictionary of metric names to values
        """
        try:
            # Generate predictions
            predictions = pipeline.predict(features)
            
            # Calculate metrics
            mse = mean_squared_error(labels, predictions)
            r2 = r2_score(labels, predictions)
            rmse = np.sqrt(mse)
            
            return {
                'mse': float(mse),
                'rmse': float(rmse),
                'r2_score': float(r2),
                'n_samples': len(features)
            }
        except Exception as e:
            # Return empty dict if metrics calculation fails
            return {'error': str(e)}