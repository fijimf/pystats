import os
import pandas as pd
from sqlalchemy import create_engine
from flask import request

class DataService:
    def __init__(self):
        self.engine = create_engine(os.getenv('DATABASE_URL'))
    
    def load_games_by_season(self, year=None, team_id=None):
        """Load games data from database with optional filtering"""
        if year is None:
            year = request.args.get('year') if request else None
        if team_id is None:
            team_id = request.args.get('team_id') if request else None
        
        base_query = """
            SELECT s.year, g.date, h.long_name home_team, h.abbreviation home_code, g.home_score, 
                   a.long_name away_team, a.abbreviation away_code, g.away_score, g.neutral_site 
            FROM game g
            INNER JOIN season s ON g.season_id = s.id
            INNER JOIN team h ON g.home_team_id = h.id
            INNER JOIN team a ON g.away_team_id = a.id
            WHERE g.home_score > 0 AND g.away_score > 0
        """
        
        conditions = []
        if year:
            conditions.append(f"s.year = {year}")
        if team_id:
            conditions.append(f"(h.id = {team_id} OR a.id = {team_id})")
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " ORDER BY date, h.long_name, a.long_name"
        
        df = pd.read_sql(base_query, self.engine)
        return df