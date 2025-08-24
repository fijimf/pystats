from flask import request
from flask_restx import Resource, fields
from app.utils.logging import get_logger

logger = get_logger(__name__)


def register_ml_routes(api, ml_training_service, ml_prediction_service, model_registry, ModelRun, db):
    """Register ML-specific API routes"""
    
    # API Models for documentation
    error_model = api.model('Error', {
        'status': fields.String(description='Error status'),
        'message': fields.String(description='Error message')
    })

    training_request_model = api.model('MLTrainingRequest', {
        'parameters': fields.Raw(description='Model-specific training parameters'),
        'features': fields.List(fields.Raw, required=True, description='Training features'),
        'labels': fields.List(fields.Raw, required=True, description='Training labels')
    })

    training_response_model = api.model('MLTrainingResponse', {
        'status': fields.String(description='Training initiation status'),
        'message': fields.String(description='Response message'),
        'model_run_id': fields.Integer(description='ID of the training run')
    })

    prediction_request_model = api.model('MLPredictionRequest', {
        'features': fields.List(fields.Raw, required=True, description='Features for prediction')
    })

    prediction_response_model = api.model('MLPredictionResponse', {
        'predictions': fields.Raw(description='Model predictions'),
        'model_run_id': fields.Integer(description='ID of the model run used'),
        'model_name': fields.String(description='Name of the model'),
        'status': fields.String(description='Prediction status')
    })

    @api.route('/ml/train')
    class MLTraining(Resource):
        @api.doc('ml_train_model')
        @api.expect(training_request_model)
        @api.marshal_with(training_response_model)
        @api.response(400, 'Bad Request', error_model)
        @api.response(500, 'Internal Server Error', error_model)
        def post(self):
            """Train a machine learning model asynchronously
            
            Initiates training for a specified model with provided features and labels.
            Training runs asynchronously and status can be checked via model run ID.
            """
            try:
                # Get query parameters
                model_name = request.args.get('model_name')
                model_run_id = request.args.get('model_run_id', type=int)
                
                if not model_name:
                    api.abort(400, status='error', message='model_name query parameter is required')
                
                if not model_run_id:
                    api.abort(400, status='error', message='model_run_id query parameter is required')
                
                # Check if model exists
                if not model_registry.is_model_available(model_name):
                    api.abort(400, status='error', message=f'Model {model_name} not available')
                
                # Validate model run exists
                model_run = ModelRun.query.get(model_run_id)
                if not model_run:
                    api.abort(400, status='error', message=f'Model run {model_run_id} not found')
                
                # Get request payload
                payload = api.payload or {}
                parameters = payload.get('parameters', {})
                features = payload.get('features', [])
                labels = payload.get('labels', [])
                
                if not features:
                    api.abort(400, status='error', message='features are required')
                
                if not labels:
                    api.abort(400, status='error', message='labels are required')
                
                # Start training
                ml_training_service.start_training(
                    model_name=model_name,
                    model_run_id=model_run_id,
                    parameters=parameters,
                    features=features,
                    labels=labels
                )
                
                return {
                    'status': 'success',
                    'message': 'Training initiated successfully',
                    'model_run_id': model_run_id
                }
                
            except ValueError as e:
                api.abort(400, status='error', message=str(e))
            except Exception as e:
                logger.error(f"Error in ML training endpoint: {e}")
                api.abort(500, status='error', message='Internal server error')

    @api.route('/ml/predict')
    class MLPrediction(Resource):
        @api.doc('ml_predict')
        @api.expect(prediction_request_model)
        @api.marshal_with(prediction_response_model)
        @api.response(400, 'Bad Request', error_model)
        @api.response(500, 'Internal Server Error', error_model)
        def post(self):
            """Generate predictions using a trained model
            
            Uses a previously trained model to generate predictions on provided features.
            The model is identified by the model_run_id query parameter.
            """
            try:
                # Get query parameters
                model_run_id = request.args.get('model_run_id', type=int)
                
                if not model_run_id:
                    api.abort(400, status='error', message='model_run_id query parameter is required')
                
                # Get request payload
                payload = api.payload or {}
                features = payload.get('features', [])
                
                if not features:
                    api.abort(400, status='error', message='features are required')
                
                # Generate predictions
                result = ml_prediction_service.predict(model_run_id, features)
                
                if result['status'] == 'error':
                    api.abort(400, status='error', message=result['error_message'])
                
                return result
                
            except ValueError as e:
                api.abort(400, status='error', message=str(e))
            except Exception as e:
                logger.error(f"Error in ML prediction endpoint: {e}")
                api.abort(500, status='error', message='Internal server error')

    @api.route('/ml/models')
    class MLModels(Resource):
        @api.doc('list_models')
        def get(self):
            """List all available ML models"""
            try:
                models = model_registry.list_models()
                return {
                    'models': models,
                    'count': len(models)
                }
            except Exception as e:
                logger.error(f"Error listing models: {e}")
                api.abort(500, status='error', message='Internal server error')

    @api.route('/ml/model_runs/<int:model_run_id>')
    class MLModelRunInfo(Resource):
        @api.doc('get_model_run_info')
        def get(self, model_run_id):
            """Get information about a specific model run"""
            try:
                info = ml_prediction_service.get_model_run_info(model_run_id)
                if 'error' in info:
                    api.abort(404, status='error', message=info['error'])
                return info
            except Exception as e:
                logger.error(f"Error getting model run info: {e}")
                api.abort(500, status='error', message='Internal server error')