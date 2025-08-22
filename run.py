#!/usr/bin/env python3
import os
from app import create_app
from app.config.settings import config
from app.utils.logging import setup_logging

# Create app instance for Gunicorn
config_name = os.getenv('FLASK_CONFIG', 'default')
config_class = config.get(config_name, config['default'])
app = create_app(config_class)
setup_logging(app)

def main():
    """Main application entry point for development"""
    print("Starting PyStats API...")
    print("Database URL: ", os.getenv('DATABASE_URL'))
    print("Swagger UI available at: /swagger/")
    
    app.run(debug=app.config.get('DEBUG', False), host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()