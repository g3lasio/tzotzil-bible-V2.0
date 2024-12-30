"""
Inicialización principal de la aplicación
"""
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from flask_cors import CORS

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
cors = CORS()

def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # Configuración por defecto
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-nevin'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            BABEL_DEFAULT_LOCALE='es',
            CORS_HEADERS='Content-Type',
            SQLALCHEMY_ENGINE_OPTIONS={
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_size': 5,
                'max_overflow': 2,
                'pool_timeout': 30
            }
        )

        # Configurar PostgreSQL
        if app.config['SQLALCHEMY_DATABASE_URI']:
            if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
                app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
    else:
        app.config.update(test_config)

    try:
        # Asegurar que existe el directorio instance
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # Inicializar extensiones
        db.init_app(app)
        migrate.init_app(app, db)
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

            # Verificar y crear tablas si no existen
            try:
                db.create_all()
                logger.info("Base de datos inicializada correctamente")
            except Exception as e:
                logger.error(f"Error inicializando base de datos: {str(e)}")
                raise

        return app

    except Exception as e:
        logger.error(f"Error en la inicialización de la aplicación: {str(e)}")
        raise

def init_db():
    """Inicializar la base de datos"""
    with create_app().app_context():
        db.create_all()