import pandas as pd
from app.services.data_service import DataService
from app.statistical.power_estimators import least_squares_power_estimator, logistic_power_estimator

class RankingService:
    def __init__(self):
        self.data_service = DataService()
    
    def get_lse_rankings(self):
        """Get least squares power rankings over time"""
        return self._calc_by_dates(least_squares_power_estimator)
    
    def get_logistic_rankings(self):
        """Get logistic regression power rankings over time"""
        return self._calc_by_dates(logistic_power_estimator)
    
    def _calc_by_dates(self, processor_func):
        """Calculate rankings for each date in the season"""
        df = self.data_service.load_games_by_season()
        
        if df.empty:
            return {}
        
        min_date = df['date'].min()
        max_date = df['date'].max()
        dates = pd.date_range(start=min_date, end=max_date, freq='D')

        team_ratings_list = {}
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            df_subset = df[pd.to_datetime(df['date']) <= pd.to_datetime(date_str)]
            
            if len(df_subset) == 0:
                continue
                
            team_ratings = processor_func(df_subset)
            team_ratings_list[date_str] = team_ratings.to_dict()
            
        return team_ratings_list