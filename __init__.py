"""
Inicialización principal de la aplicación
"""
import os
import logging
from flask import Flask, session # Added session import
from flask_babel import Babel
from flask_cors import CORS
from flask_login import LoginManager # Added import for LoginManager
from extensions import db, migrate, configure_database, init_extensions, mail #Added mail import
from flask_mail import Mail # Added Mail import

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
babel = Babel()
cors = CORS()
login_manager = LoginManager() # Initialize LoginManager
mail = Mail() # Initialize Flask-Mail


def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para manejar sesiones
    
    from auth import login_manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
    login_manager.login_message_category = 'info'

    # Configuración base
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-nevin'),
        BABEL_DEFAULT_LOCALE='es',
        CORS_HEADERS='Content-Type',
        MAIL_SERVER='smtp.gmail.com', #Example configuration, needs to be adapted
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
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
        login_manager.init_app(app) # Initialize login_manager with the app
        login_manager.login_view = 'auth.login' # Set the login view
        mail.init_app(app) # Initialize Flask-Mail

        # Registrar blueprints
        with app.app_context():
            from routes import routes
            from nevin_routes import nevin_bp
            from auth import auth, init_login_manager

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