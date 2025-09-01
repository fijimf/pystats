import pickle
import threading
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from flask import current_app
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MLTrainingService:
    """Service for handling ML model training"""
    
    def __init__(self, db, ModelRun, ModelRunMetric, model_registry):
        self.db = db
        self.ModelRun = ModelRun
        self.ModelRunMetric = ModelRunMetric
        self.model_registry = model_registry
    
    def start_training(self, model_name: str, model_run_id: int, 
                      parameters: Dict[str, Any], features: List[Dict[str, Any]], 
                      labels: List[Dict[str, Any]]) -> None:
        """
        Start asynchronous model training.
        
        Args:
            model_name: Name of the model to train
            model_run_id: ID of the model run record
            parameters: Training parameters
            features: Training features
            labels: Training labels
        """
        logger.info(f"Starting training for model {model_name}, run_id {model_run_id}")
        
        # Capture the current app context
        app = current_app._get_current_object()
        
        # Start training in background thread
        training_thread = threading.Thread(
            target=self._train_model_with_context,
            args=(app, model_name, model_run_id, parameters, features, labels),
            name=f"training-{model_name}-{model_run_id}"
        )
        training_thread.daemon = True
        training_thread.start()
    
    def _train_model_with_context(self, app, model_name: str, model_run_id: int,
                                 parameters: Dict[str, Any], features: List[Dict[str, Any]], 
                                 labels: List[Dict[str, Any]]) -> None:
        """
        Wrapper method that runs training within Flask app context.
        
        Args:
            app: Flask application instance
            model_name: Name of the model to train
            model_run_id: ID of the model run record
            parameters: Training parameters
            features: Training features
            labels: Training labels
        """
        with app.app_context():
            self._train_model(model_name, model_run_id, parameters, features, labels)
    
    def _train_model(self, model_name: str, model_run_id: int,
                    parameters: Dict[str, Any], features: List[Dict[str, Any]], 
                    labels: List[Dict[str, Any]]) -> None:
        """
        Internal method for training model in background thread.
        
        Args:
            model_name: Name of the model to train
            model_run_id: ID of the model run record
            parameters: Training parameters
            features: Training features
            labels: Training labels
        """
        try:
            # Update run status to RUNNING
            self._update_run_status(model_run_id, 'RUNNING')
            
            # Get model instance
            model = self.model_registry.get_model(model_name)
            
            # Validate features and labels
            if not model.validate_features(features):
                raise ValueError(f"Invalid features for model {model_name}")
            
            if not model.validate_labels(labels):
                raise ValueError(f"Invalid labels for model {model_name}")
            
            # Convert features and labels to training format
            X, y = self._prepare_training_data(features, labels, model)
            
            # Create and train pipeline
            pipeline = model.create_pipeline(parameters)
            pipeline.fit(X, y)
            
            # Extract metrics
            metrics = model.extract_metrics(pipeline, X, y)
            
            # Pickle the trained pipeline
            pickled_pipeline = pickle.dumps(pipeline)
            
            # Save results to database
            self._save_training_results(model_run_id, pickled_pipeline, metrics)
            
            # Update run status to SUCCESS
            self._update_run_status(model_run_id, 'SUCCESS')
            
            logger.info(f"Training completed successfully for model {model_name}, run_id {model_run_id}")
            
        except Exception as e:
            logger.error(f"Training failed for model {model_name}, run_id {model_run_id}: {e}")
            self._update_run_status(model_run_id, 'FAILED')
            
            # Save error details as metrics
            self._save_error_metrics(model_run_id, str(e))
    
    def _prepare_training_data(self, features: List[Dict[str, Any]], 
                             labels: List[Dict[str, Any]], model) -> tuple:
        """
        Convert feature and label dictionaries to training format.
        
        Args:
            features: List of feature dictionaries
            labels: List of label dictionaries
            model: Model instance for feature/label validation
            
        Returns:
            Tuple of (X, y) for training
        """
        # Convert features to DataFrame
        features_df = pd.DataFrame(features)
        X = features_df[model.feature_names]
        
        # Convert labels to appropriate format
        labels_df = pd.DataFrame(labels)
        
        if len(model.label_names) == 1:
            # Single target variable
            y = labels_df[model.label_names[0]]
        else:
            # Multiple target variables
            y = labels_df[model.label_names]
        
        return X, y
    
    def _update_run_status(self, model_run_id: int, status: str) -> None:
        """Update model run status in database"""
        try:
            model_run = self.ModelRun.query.get(model_run_id)
            if model_run:
                model_run.run_status = status
                if status in ['SUCCESS', 'FAILED']:
                    model_run.run_date = datetime.utcnow()
                self.db.session.commit()
            else:
                logger.error(f"Model run {model_run_id} not found")
        except Exception as e:
            logger.error(f"Error updating run status: {e}")
            self.db.session.rollback()
    
    def _save_training_results(self, model_run_id: int, pickled_pipeline: bytes, 
                             metrics: Dict[str, float]) -> None:
        """Save training results and metrics to database"""
        try:
            # Save pickled pipeline
            model_run = self.ModelRun.query.get(model_run_id)
            if model_run:
                model_run.run_result = pickled_pipeline
            
            # Save metrics
            for metric_name, metric_value in metrics.items():
                metric = self.ModelRunMetric(
                    model_run_id=model_run_id,
                    metric_name=metric_name,
                    metric_value=str(metric_value)
                )
                self.db.session.add(metric)
            
            self.db.session.commit()
            logger.info(f"Saved training results for run {model_run_id}")
            
        except Exception as e:
            logger.error(f"Error saving training results: {e}")
            self.db.session.rollback()
    
    def _save_error_metrics(self, model_run_id: int, error_message: str) -> None:
        """Save error details as metrics"""
        try:
            error_metric = self.ModelRunMetric(
                model_run_id=model_run_id,
                metric_name='error',
                metric_value=error_message[:255]  # Truncate to fit in VARCHAR(255)
            )
            self.db.session.add(error_metric)
            self.db.session.commit()
        except Exception as e:
            logger.error(f"Error saving error metrics: {e}")
            self.db.session.rollback()