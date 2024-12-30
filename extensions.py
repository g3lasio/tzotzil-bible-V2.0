"""
Centralized extensions configuration
"""
import os
import time
import logging
from datetime import datetime
from flask import request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize extensions without binding to app yet
db = SQLAlchemy()
migrate = Migrate()

def configure_database(app):
    """Configure database connection and initialize extensions."""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # Configure SQLAlchemy
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_size': 5,
                'max_overflow': 2,
                'pool_timeout': 30
            }
        })

        # Initialize extensions
        db.init_app(app)
        migrate.init_app(app, db)

        # Verify database connection
        with app.app_context():
            db.create_all()
            db.session.execute(text('SELECT 1')).scalar()
            logger.info("Database connection verified successfully")

        return True

    except Exception as e:
        logger.error(f"Database configuration error: {str(e)}")
        if hasattr(db, 'session'):
            db.session.remove()
        if hasattr(db, 'engine'):
            db.engine.dispose()
        return False

def init_extensions(app):
    """Initialize all Flask extensions"""
    try:
        if not configure_database(app):
            raise Exception("Failed to configure database")

        logger.info("All extensions initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Extension initialization error: {str(e)}")
        return False

def get_locale():
    """Get locale for babel"""
    if request and 'language' in request.args:
        return request.args['language']
    return request.accept_languages.best_match(['en', 'es', 'tz'])