import pickle
from typing import Dict, List, Any
import pandas as pd
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MLPredictionService:
    """Service for handling ML model predictions"""
    
    def __init__(self, db, ModelRun, model_registry):
        self.db = db
        self.ModelRun = ModelRun
        self.model_registry = model_registry
    
    def predict(self, model_run_id: int, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate predictions using a trained model.
        
        Args:
            model_run_id: ID of the trained model run
            features: Features for prediction
            
        Returns:
            Dictionary containing predictions and metadata
        """
        logger.info(f"Starting prediction for model_run_id {model_run_id}")
        
        try:
            # Get the model run from database
            model_run = self._get_model_run(model_run_id)
            
            # Validate model run
            if model_run.run_status != 'SUCCESS':
                raise ValueError(f"Model run {model_run_id} is not in SUCCESS status: {model_run.run_status}")
            
            if not model_run.run_result:
                raise ValueError(f"No trained pipeline found for model run {model_run_id}")
            
            # Get model instance for validation
            model = self.model_registry.get_model(model_run.model.name)
            
            # Validate features
            if not model.validate_features(features):
                raise ValueError(f"Invalid features for model {model_run.model.name}")
            
            # Prepare features for prediction
            X = self._prepare_prediction_features(features, model)
            
            # Load and deserialize the trained pipeline
            pipeline = pickle.loads(model_run.run_result)
            
            # Generate predictions
            predictions = pipeline.predict(X)
            
            # Format predictions for response
            prediction_results = self._format_predictions(predictions)
            
            logger.info(f"Prediction completed for model_run_id {model_run_id}")
            
            return {
                'predictions': prediction_results,
                'model_run_id': model_run_id,
                'model_name': model_run.model.name,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Prediction failed for model_run_id {model_run_id}: {e}")
            return {
                'predictions': None,
                'model_run_id': model_run_id,
                'status': 'error',
                'error_message': str(e)
            }
    
    def _get_model_run(self, model_run_id: int):
        """Get model run from database with model information"""
        model_run = self.ModelRun.query.filter_by(id=model_run_id).first()
        if not model_run:
            raise ValueError(f"Model run {model_run_id} not found")
        return model_run
    
    def _prepare_prediction_features(self, features: List[Dict[str, Any]], model) -> pd.DataFrame:
        """
        Prepare features for prediction.
        
        Args:
            features: List of feature dictionaries
            model: Model instance for feature validation
            
        Returns:
            DataFrame with features ready for prediction
        """
        # Convert features to DataFrame
        features_df = pd.DataFrame(features)
        
        # Select only the required features in the correct order
        X = features_df[model.feature_names]
        
        return X
    
    def _format_predictions(self, predictions) -> List[Any]:
        """
        Format predictions for JSON response.
        
        Args:
            predictions: Raw predictions from sklearn pipeline
            
        Returns:
            List of formatted predictions
        """
        if hasattr(predictions, 'tolist'):
            # numpy array
            return predictions.tolist()
        elif hasattr(predictions, 'values'):
            # pandas Series/DataFrame
            return predictions.values.tolist()
        else:
            # already a list or other serializable format
            return list(predictions)
    
    def get_model_run_info(self, model_run_id: int) -> Dict[str, Any]:
        """
        Get information about a model run.
        
        Args:
            model_run_id: ID of the model run
            
        Returns:
            Dictionary with model run information
        """
        try:
            model_run = self._get_model_run(model_run_id)
            return {
                'model_run_id': model_run.id,
                'model_name': model_run.model.name,
                'model_type': model_run.model.type,
                'run_status': model_run.run_status,
                'run_date': model_run.run_date.isoformat() if model_run.run_date else None,
                'has_trained_pipeline': model_run.run_result is not None
            }
        except Exception as e:
            logger.error(f"Error getting model run info for {model_run_id}: {e}")
            return {'error': str(e)}