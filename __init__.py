import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from auth import auth, init_login_manager
from routes import init_routes
from extensions import init_extensions
from nevin_routes import init_nevin_routes

# Configuración mejorada de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Inicializar y configurar la aplicación Flask"""
    app = Flask(__name__)

    try:
        # Configuración básica
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-nevin')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_recycle': 300,
            'pool_pre_ping': True
        }

        logger.info(f"Usando base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Inicializar CORS
        CORS(app)

        # Inicializar extensiones
        if not init_extensions(app):
            logger.error("Error inicializando extensiones")
            return None
        logger.info("Extensiones inicializadas correctamente")

        # Inicializar migración después de las extensiones
        migrate = Migrate(app, db)

        # Registrar blueprints
        app.register_blueprint(auth, url_prefix='/api')
        init_routes(app)
        init_nevin_routes(app)  # Inicializar rutas de Nevin
        logger.info("Blueprints registrados correctamente")

        # Inicializar login manager
        init_login_manager(app)
        logger.info("Login manager inicializado correctamente")

        # Manejar el error 404
        @app.errorhandler(404)
        def not_found_error(error):
            logger.warning(f"Página no encontrada: {error}")
            return "Página no encontrada", 404

        return app
    except Exception as e:
        logger.error(f"Error creando la aplicación: {str(e)}")
        return None

def main():
    app = create_app()
    if app:
        port = int(os.environ.get('PORT', 8080)) # Changed default port to 8080
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        logger.error("No se pudo iniciar la aplicación")
        exit(1)

if __name__ == '__main__':
    main()