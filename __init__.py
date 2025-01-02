import os
import logging
from flask import Flask
from flask_cors import CORS
from models import db
from auth import auth, init_login_manager
from routes import init_routes
from extensions import init_extensions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Inicializar y configurar la aplicación Flask"""
    app = Flask(__name__)

    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-nevin')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    logger.info(f"Usando base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Inicializar CORS
    CORS(app)

    try:
        # Inicializar extensiones
        init_extensions(app)
        logger.info("Extensiones inicializadas correctamente")

        # Registrar blueprints
        app.register_blueprint(auth, url_prefix='/api')
        init_routes(app)
        logger.info("Blueprints registrados correctamente")

        # Inicializar login manager
        init_login_manager(app)
        logger.info("Login manager inicializado correctamente")

        return app
    except Exception as e:
        logger.error(f"Error creando la aplicación: {str(e)}")
        return None

def main():
    app = create_app()
    if app:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        logger.error("No se pudo iniciar la aplicación")

if __name__ == '__main__':
    main()