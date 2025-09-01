from flask_restx import Resource, fields
from app.services.ranking_service import RankingService

def register_ranking_routes(api):
    error_model = api.model('Error', {
        'status': fields.String(description='Error status'),
        'message': fields.String(description='Error message')
    })

    rankings_response_model = api.model('RankingsResponse', {
        'status': fields.String(description='Response status'),
        'data': fields.Raw(description='Team rankings data by date')
    })

    ranking_service = RankingService()

    @api.route('/rankings/lse')
    class LSERankings(Resource):
        @api.doc('get_lse_rankings')
        @api.marshal_with(rankings_response_model)
        @api.response(500, 'Internal Server Error', error_model)
        def get(self):
            """Get least squares power rankings over time
            
            Returns team power rankings calculated using least squares estimation,
            computed for each date in the current season.
            """
            try:
                team_ratings_list = ranking_service.get_lse_rankings()
                return {
                    'status': 'success',
                    'data': team_ratings_list
                }
            except Exception as e:
                api.abort(500, status='error', message=str(e))

    @api.route('/rankings/logistic')
    class LogisticRankings(Resource):
        @api.doc('get_logistic_rankings')
        @api.marshal_with(rankings_response_model)
        @api.response(500, 'Internal Server Error', error_model)
        def get(self):
            """Get logistic regression power rankings over time
            
            Returns team power rankings calculated using logistic regression,
            computed for each date in the current season.
            """
            try:
                team_ratings_list = ranking_service.get_logistic_rankings()
                return {
                    'status': 'success',
                    'data': team_ratings_list
                }
            except Exception as e:
                api.abort(500, status='error', message=str(e))