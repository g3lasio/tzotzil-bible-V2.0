
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_babel import Babel
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
babel = Babel()
cors = CORS()

def init_extensions(app):
    """Inicializar extensiones de Flask"""
    try:
        cors.init_app(app)
        db.init_app(app)
        migrate.init_app(app, db)
        mail.init_app(app)
        babel.init_app(app)
        
        with app.app_context():
            db.create_all()
            
        return True
    except Exception as e:
        logger.error(f"Error inicializando extensiones: {str(e)}")
        return False
