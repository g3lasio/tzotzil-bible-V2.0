"""
Módulo principal para inicialización y gestión de la aplicación
"""
import os
import logging
from flask import Flask
from extensions import db, init_extensions
from datetime import timedelta

# Configuración de logging
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
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-static-secret-key-here')
        app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
        logger.info("SECRET_KEY configurada correctamente")
        
        # Autenticación deshabilitada - acceso libre para todos los usuarios
        # @app.before_request 
        # def require_auth(): # Comentado para acceso libre
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_recycle': 300,
            'pool_pre_ping': True
        }

        logger.info(f"Usando base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Inicializar extensiones
        if not init_extensions(app):
            logger.error("Error inicializando extensiones")
            return None

        # Importar modelos después de inicializar db
        from models import User, BibleVerse, Promise

        # Registrar blueprints
        from auth import auth, init_login_manager
        app.register_blueprint(auth, url_prefix='/api/auth')

        # Importar e inicializar rutas después de los modelos
        from routes import init_routes
        from nevin_routes import init_nevin_routes

        init_routes(app)
        init_nevin_routes(app)
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
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        logger.error("No se pudo iniciar la aplicación")
        exit(1)

if __name__ == '__main__':
    main()