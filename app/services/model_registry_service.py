import os
import importlib
import inspect
from typing import Dict, List, Type
from app.statistical.model_interface import ModelInterface
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ModelRegistryService:
    """Service for managing the ML model registry"""
    
    def __init__(self, db, Model):
        self.db = db
        self.Model = Model
        self._models: Dict[str, ModelInterface] = {}
    
    def scan_and_sync_models(self) -> None:
        """Scan statistical directory and sync with database"""
        logger.info("Starting model registry scan and sync")
        
        # Scan for model classes
        self._scan_statistical_directory()
        
        # Sync with database
        self._sync_with_database()
        
        logger.info(f"Model registry sync completed. Found {len(self._models)} models")
    
    def _scan_statistical_directory(self) -> None:
        """Scan the app/statistical directory for model classes"""
        statistical_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statistical')
        
        if not os.path.exists(statistical_path):
            logger.warning(f"Statistical directory not found: {statistical_path}")
            return
        
        for filename in os.listdir(statistical_path):
            if filename.endswith('.py') and not filename.startswith('__') and filename != 'model_interface.py':
                module_name = filename[:-3]
                try:
                    self._load_models_from_module(module_name)
                except Exception as e:
                    logger.error(f"Error loading models from {module_name}: {e}")
    
    def _load_models_from_module(self, module_name: str) -> None:
        """Load model classes from a specific module"""
        try:
            module = importlib.import_module(f'app.statistical.{module_name}')
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, ModelInterface) and 
                    obj != ModelInterface and 
                    not inspect.isabstract(obj)):
                    
                    model_instance = obj()
                    self._models[model_instance.name] = model_instance
                    logger.info(f"Loaded model: {model_instance.name} from {module_name}")
                    
        except Exception as e:
            logger.error(f"Error importing module {module_name}: {e}")
    
    def _sync_with_database(self) -> None:
        """Sync discovered models with database registry"""
        try:
            # Get all models from database
            db_models = {model.name: model for model in self.Model.query.all()}
            
            # Check each discovered model
            for model_name, model_instance in self._models.items():
                db_model = db_models.get(model_name)
                
                if db_model:
                    # Model exists in both - update pipeline_ok status
                    db_model.pipeline_ok = True
                    db_model.features_ok = True  # Assume features are ok if model is loaded
                    logger.info(f"Updated model {model_name}: pipeline_ok=True")
                else:
                    # Model only in code - log warning (don't auto-create)
                    logger.warning(f"Model {model_name} exists in code but not in database")
            
            # Check for models in database but not in code
            for db_model_name, db_model in db_models.items():
                if db_model_name not in self._models:
                    db_model.pipeline_ok = False
                    db_model.features_ok = False
                    logger.warning(f"Model {db_model_name} exists in database but not in code: pipeline_ok=False")
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Error syncing with database: {e}")
            self.db.session.rollback()
    
    def get_model(self, model_name: str) -> ModelInterface:
        """Get a model instance by name"""
        model = self._models.get(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found in registry")
        return model
    
    def list_models(self) -> List[str]:
        """List all available model names"""
        return list(self._models.keys())
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if model is available in registry"""
        return model_name in self._models