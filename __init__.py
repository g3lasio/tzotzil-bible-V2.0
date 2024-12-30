"""
Inicialización principal de la aplicación
"""
import os
import logging
from flask import Flask
from flask_babel import Babel
from flask_cors import CORS
# Added import for new module
from extensions import db, migrate, configure_database

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
babel = Babel()
cors = CORS()

def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__)

    # Configuración base
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-nevin'),
        BABEL_DEFAULT_LOCALE='es',
        CORS_HEADERS='Content-Type'
    )

    if test_config:
        app.config.update(test_config)

    try:
        # Configure database - this replaces the old database configuration section
        if not configure_database(app):
            raise Exception("Failed to configure database")

        # Initialize other extensions
        babel.init_app(app)
        cors.init_app(app)

        with app.app_context():
            # Import and register blueprints
            from routes import routes
            from nevin_routes import nevin_bp
            from auth import auth

            app.register_blueprint(routes)
            app.register_blueprint(nevin_bp, url_prefix='/nevin')
            app.register_blueprint(auth)

            logger.info("Application initialized successfully")
            return app

    except Exception as e:
        logger.error(f"Error in application initialization: {str(e)}")
        raise