"""
Inicialización principal de la aplicación
"""
import os
import logging
from flask import Flask
from flask_babel import Babel
from flask_cors import CORS
from extensions import db, migrate, configure_database, init_extensions

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
babel = Babel()
cors = CORS()

def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)

    # Configuración base
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-nevin'),
        BABEL_DEFAULT_LOCALE='es',
        CORS_HEADERS='Content-Type'
    )

    if test_config:
        app.config.update(test_config)

    try:
        # Asegurar que existe el directorio instance
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # Inicializar extensiones incluyendo la base de datos
        if not init_extensions(app):
            raise Exception("Failed to initialize extensions")

        # Inicializar otras extensiones
        babel.init_app(app)
        cors.init_app(app)

        # Registrar blueprints
        with app.app_context():
            from routes import routes
            from nevin_routes import nevin_bp
            from auth import auth

            app.register_blueprint(routes)
            app.register_blueprint(nevin_bp, url_prefix='/nevin')
            app.register_blueprint(auth)

            logger.info("Application initialized successfully")

        return app

    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        raise

def init_db():
    """Initialize the database"""
    with create_app().app_context():
        db.create_all()