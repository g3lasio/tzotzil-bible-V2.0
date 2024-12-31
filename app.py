
import os
import logging
from flask import Flask
from extensions import init_extensions
from routes import init_routes
from nevin_routes import init_nevin_routes, nevin_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    
    try:
        logger.info("Iniciando configuración de la aplicación...")
        
        # Configuración básica
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/bible_app.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 30,
            'pool_size': 30,
            'max_overflow': 10
        }
        
        # Inicializar extensiones y base de datos
        from extensions import db, init_extensions
        db.init_app(app)
        
        with app.app_context():
            try:
                db.create_all()
                logger.info("Base de datos inicializada")
                
                if not init_extensions(app):
                    logger.error("Error inicializando extensiones")
                    return None
                    
                # Verificar conexión
                db.session.execute(text('SELECT 1'))
                logger.info("Conexión a base de datos verificada")
                
            except Exception as e:
                logger.error(f"Error crítico en inicialización: {str(e)}")
                return None
            
        # Registrar rutas
        init_routes(app)
        init_nevin_routes(app)
        
        return app
        
    except Exception as e:
        logger.error(f"Error crítico creando la aplicación: {str(e)}")
        return None

if __name__ == '__main__':
    app = create_app()
    if app:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    else:
        logger.error("No se pudo iniciar la aplicación")
