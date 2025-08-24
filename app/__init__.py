from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api

from app.config.settings import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    # Create API instance
    api = Api(
        title='PyStats API',
        version='1.0',
        description='Statistical analysis API for sports data with machine learning capabilities',
        doc='/swagger/',
        prefix='/api'
    )
    api.init_app(app)
    
    with app.app_context():
        db.Model.metadata.reflect(bind=db.engine)
        from app.models.team_statistic import create_models
        create_models(db)
        
        # Create ML models
        from app.models.ml_models import create_ml_models
        Model, ModelRun, ModelRunMetric = create_ml_models(db)
        
        # Initialize ML services
        from app.services.model_registry_service import ModelRegistryService
        from app.services.ml_training_service import MLTrainingService
        from app.services.ml_prediction_service import MLPredictionService
        
        # Create ML service instances
        model_registry = ModelRegistryService(db, Model)
        ml_training_service = MLTrainingService(db, ModelRun, ModelRunMetric, model_registry)
        ml_prediction_service = MLPredictionService(db, ModelRun, model_registry)
        
        # Scan and sync models on startup
        model_registry.scan_and_sync_models()
    
        # Register API routes
        from app.api.health import register_health_routes
        from app.api.rankings import register_ranking_routes
        from app.api.training import register_training_routes
        from app.api.ml import register_ml_routes
        
        register_health_routes(api)
        register_ranking_routes(api)
        register_training_routes(api)
        register_ml_routes(api, ml_training_service, ml_prediction_service, model_registry, ModelRun, db)
    
    return app