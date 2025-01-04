"""
Centraliza la configuración de extensiones de Flask
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_babel import Babel
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
babel = Babel()
cors = CORS()

def init_extensions(app):
    """Inicializa todas las extensiones de Flask"""
    try:
        # Inicializar SQLAlchemy
        db.init_app(app)

        # Inicializar las demás extensiones
        migrate.init_app(app, db)
        mail.init_app(app)
        babel.init_app(app)
        cors.init_app(app)

        logger.info("Extensiones inicializadas correctamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando extensiones: {str(e)}")
        return False