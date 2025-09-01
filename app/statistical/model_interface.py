from abc import ABC, abstractmethod
from typing import Dict, List, Any
from sklearn.pipeline import Pipeline


class ModelInterface(ABC):
    """Abstract base class for all ML models in the statistical package."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the model."""
        pass
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Type of model (e.g., 'regression', 'classification', 'clustering')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the model."""
        pass
    
    @property
    @abstractmethod
    def feature_names(self) -> List[str]:
        """List of expected feature column names."""
        pass
    
    @property
    @abstractmethod
    def label_names(self) -> List[str]:
        """List of expected label column names."""
        pass
    
    @abstractmethod
    def create_pipeline(self, parameters: Dict[str, Any]) -> Pipeline:
        """
        Create sklearn Pipeline with given parameters.
        
        Args:
            parameters: Dictionary of model-specific parameters
            
        Returns:
            Configured sklearn Pipeline ready for training
        """
        pass
    
    @abstractmethod
    def get_default_parameters(self) -> Dict[str, Any]:
        """
        Return default parameter values for the model.
        
        Returns:
            Dictionary of default parameters
        """
        pass
    
    def validate_features(self, features: List[Dict[str, Any]]) -> bool:
        """
        Validate input feature format matches expected schema.
        
        Args:
            features: List of feature dictionaries
            
        Returns:
            True if features are valid, False otherwise
        """
        if not features:
            return False
        
        required_features = set(self.feature_names)
        feature_keys = set(features[0].keys())
        
        return required_features.issubset(feature_keys)
    
    def validate_labels(self, labels: List[Dict[str, Any]]) -> bool:
        """
        Validate input label format matches expected schema.
        
        Args:
            labels: List of label dictionaries
            
        Returns:
            True if labels are valid, False otherwise
        """
        if not labels:
            return False
        
        required_labels = set(self.label_names)
        label_keys = set(labels[0].keys())
        
        return required_labels.issubset(label_keys)
    
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
        return {}