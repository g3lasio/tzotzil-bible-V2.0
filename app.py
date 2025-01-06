import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from database import db_manager
from routes import init_routes
from extensions import init_extensions
from error_handlers import register_error_handlers
from db_monitor import db_monitor
import logging
from nevin_routes import init_nevin_routes  # Importar las rutas de Nevin

def create_app():
    app = Flask(__name__)

    # Configuración CORS actualizada para React Native
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://sistema-nevin.replit.app", 
                       "https://tzotzil-bible-reader.replit.app",
                       "http://localhost:19006",  # Para desarrollo de React Native/Expo
                       "exp://localhost:19000"],  # Para desarrollo de Expo
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configurar la aplicación
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev_key_only_for_development")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Registrar manejadores de errores
    register_error_handlers(app)

    # Inicializar extensiones
    if not init_extensions(app):
        logger.error("Error al inicializar las extensiones")
        return None

    # Inicializar monitor de base de datos
    db_monitor.init_app(app)
    db_monitor.start()

    # Inicializar rutas principales
    init_routes(app)

    # Inicializar rutas de Nevin
    init_nevin_routes(app)

    @app.route('/api/health')
    def health_check():
        db_status = db_monitor.get_status()
        return jsonify({
            "status": "healthy" if db_status['is_healthy'] else "unhealthy",
            "version": "1.0.0",
            "debug": app.debug,
            "database": db_status
        })

    return app

# Para ejecución directa del archivo
if __name__ == '__main__':
    app = create_app()
    if app is None:
        sys.exit(1)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)