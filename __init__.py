"""
Inicialización principal de la aplicación
"""
import os
import logging
from flask import Flask
from flask_babel import Babel
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from extensions import db, migrate, init_extensions

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
babel = Babel()
cors = CORS()
login_manager = LoginManager()
mail = Mail()

def create_app(test_config=None):
    """Create and configure the app"""
    try:
        app = Flask(__name__, instance_relative_config=True)

        # Configuración base
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-nevin'),
            BABEL_DEFAULT_LOCALE='es',
            CORS_HEADERS='Content-Type',
            MAIL_SERVER='smtp.gmail.com',
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
            MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
        )

        # Configurar Database URL
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 30,
            'pool_size': 30,
            'max_overflow': 10,
            'connect_args': {
                'connect_timeout': 10,
                'options': '-c statement_timeout=60000'
            },
            'echo': True  # Para debugging
        }

        if test_config:
            app.config.update(test_config)

        try:
            # Asegurar que existe el directorio instance
            try:
                os.makedirs(app.instance_path)
            except OSError:
                pass

            # Inicializar login manager primero
            from auth import init_login_manager
            init_login_manager(app)

            # Inicializar extensiones
            if not init_extensions(app):
                logger.error("Falló la inicialización de extensiones")
                raise Exception("Failed to initialize extensions")

            # Inicializar otras extensiones
            babel.init_app(app)
            cors.init_app(app)
            mail.init_app(app)

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
            logger.error(f"Error inicializando la aplicación: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Error crítico creando la aplicación: {str(e)}")
        return None

if __name__ == '__main__':
    app = create_app()
    if app:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        logger.error("No se pudo iniciar la aplicación")