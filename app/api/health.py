from flask_restx import Resource, fields

def register_health_routes(api):
    health_model = api.model('Health', {
        'status': fields.String(description='API health status'),
        'message': fields.String(description='Health check message')
    })

    @api.route('/health')
    class HealthCheck(Resource):
        @api.doc('health_check')
        @api.marshal_with(health_model)
        def get(self):
            """Health check endpoint"""
            return {
                'status': 'healthy',
                'message': 'PyStats API is running'
            }