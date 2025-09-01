from datetime import datetime
from sqlalchemy import MetaData

def create_models(db):
    """Create model classes with the given db instance"""
    
    class TeamStatistic(db.Model):
        """Model mapped to an existing table"""
        __tablename__ = 'team_statistic'

        # Explicitly define the primary key while letting SQLAlchemy reflect other columns
        id = db.Column(db.Integer, primary_key=True)
        __table_args__ = {'extend_existing': True}

        def __repr__(self):
            return f'<TeamStatistic {self.id}: {self.value}>'

        def to_dict(self):
            return {
                'id': self.id,
                'team_id': self.team_id,
                'stat_type': self.stat_type,
                'value': self.value,
                'timestamp': self.timestamp.isoformat() if hasattr(self, 'timestamp') and self.timestamp else None
            }
    
    return TeamStatistic