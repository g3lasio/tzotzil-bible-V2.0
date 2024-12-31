
import os
import logging
from flask import Flask
from extensions import init_extensions
from routes import init_routes
from nevin_routes import init_nevin_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    try:
        # Configuración básica
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bible_app.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    
    # Inicializar extensiones
    if not init_extensions(app):
        logger.error("Error inicializando extensiones")
        return None
        
    # Registrar rutas
    init_routes(app)
    init_nevin_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    if app:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    else:
        logger.error("No se pudo iniciar la aplicación")
