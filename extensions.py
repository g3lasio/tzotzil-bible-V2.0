from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_babel import Babel
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
babel = Babel()
cors = CORS(resources={
    r"/api/*": {
        "origins": [
            "https://*.replit.app",
            "https://*.replit.dev",
            "http://localhost:19006",  # Para desarrollo local de React Native/Expo
            "http://localhost:8083",   # Para Expo development server
            "http://localhost:3000",   # Para web-deploy script
            "exp://localhost:19000"    # Para Expo desarrollo con QR
        ],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Cache-Control"
        ],
        "expose_headers": [
            "Content-Range",
            "X-Total-Count",
            "X-Rate-Limit-Remaining"
        ],
        "supports_credentials": True,
        "max_age": 3600,
        "send_wildcard": False
    }
})

def init_extensions(app):
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        mail.init_app(app)
        babel.init_app(app)
        cors.init_app(app)

        logger.info("Extensiones inicializadas correctamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando extensiones: {str(e)}")
        return False