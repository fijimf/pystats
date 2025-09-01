from flask_restx import Resource, fields
from app.services.training_service import TrainingService

def register_training_routes(api):
    error_model = api.model('Error', {
        'status': fields.String(description='Error status'),
        'message': fields.String(description='Error message')
    })

    training_request_model = api.model('TrainingRequest', {
        'features': fields.Raw(required=True, description='Feature data for training'),
        'targets': fields.Raw(required=True, description='Target data for training'),
        'key': fields.String(required=True, description='Model type key (basic-margin, neural)'),
        'asOf': fields.String(required=True, description='Training date/version identifier')
    })

    training_response_model = api.model('TrainingResponse', {
        'status': fields.String(description='Training status'),
        'message': fields.String(description='Training result message'),
        'pipeline': fields.String(description='Saved pipeline filename')
    })

    training_service = TrainingService()

    @api.route('/train')
    class ModelTraining(Resource):
        @api.doc('train_model')
        @api.expect(training_request_model)
        @api.marshal_with(training_response_model)
        @api.response(500, 'Internal Server Error', error_model)
        def post(self):
            """Train a machine learning model with provided data
            
            Accepts training features and targets to create and save a ML pipeline.
            Supports different model types specified by the 'key' parameter.
            """
            try:
                payload = api.payload
                result = training_service.train_model(
                    features=payload['features'],
                    targets=payload['targets'],
                    key=payload['key'],
                    as_of=payload['asOf']
                )
                return result
            except Exception as e:
                api.abort(500, status='error', message=str(e))