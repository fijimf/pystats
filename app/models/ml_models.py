from datetime import datetime


def create_ml_models(db):
    """Create ML model classes with the given db instance"""
    
    class Model(db.Model):
        """Model registry table"""
        __tablename__ = 'models'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255), nullable=False, unique=True)
        type = db.Column(db.String(255), nullable=False)
        description = db.Column(db.String(1023))
        class_name = db.Column(db.String(511), nullable=False)
        pipeline = db.Column(db.LargeBinary)
        features_ok = db.Column(db.Boolean, nullable=False, default=False)
        pipeline_ok = db.Column(db.Boolean, nullable=False, default=False)
        
        def __repr__(self):
            return f'<Model {self.name}: {self.type}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'type': self.type,
                'description': self.description,
                'class_name': self.class_name,
                'features_ok': self.features_ok,
                'pipeline_ok': self.pipeline_ok
            }
    
    class ModelRun(db.Model):
        """Model training runs table"""
        __tablename__ = 'model_runs'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        model_id = db.Column(db.BigInteger, db.ForeignKey('models.id'), nullable=False)
        run_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        run_status = db.Column(db.String(255), nullable=False)
        run_result = db.Column(db.LargeBinary)
        
        # Relationship
        model = db.relationship('Model', backref=db.backref('runs', lazy=True))
        
        def __repr__(self):
            return f'<ModelRun {self.id}: {self.run_status}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'model_id': self.model_id,
                'run_date': self.run_date.isoformat() if self.run_date else None,
                'run_status': self.run_status,
                'model_name': self.model.name if self.model else None
            }
    
    class ModelRunMetric(db.Model):
        """Model training metrics table"""
        __tablename__ = 'model_run_metrics'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        model_run_id = db.Column(db.BigInteger, db.ForeignKey('model_runs.id'), nullable=False)
        metric_name = db.Column(db.String(255))
        metric_value = db.Column(db.String(255))
        
        # Relationship
        model_run = db.relationship('ModelRun', backref=db.backref('metrics', lazy=True))
        
        def __repr__(self):
            return f'<ModelRunMetric {self.metric_name}: {self.metric_value}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'model_run_id': self.model_run_id,
                'metric_name': self.metric_name,
                'metric_value': self.metric_value
            }
    
    return Model, ModelRun, ModelRunMetric