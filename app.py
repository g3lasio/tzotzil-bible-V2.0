import os
import sys
import logging
from flask import Flask, jsonify
from database import db_manager
from routes import init_routes
from extensions import init_extensions
from error_handlers import register_error_handlers
from db_monitor import db_monitor
from nevin_routes import init_nevin_routes
from auth import init_auth_routes

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    from auth import init_login_manager
    init_login_manager(app)

    # CORS se configura en extensions.py para evitar duplicación

    # Configurar la aplicación
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev_key_only_for_development")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    try:
        # Registrar manejadores de errores
        register_error_handlers(app)
        logger.info("Manejadores de errores registrados")

        # Inicializar extensiones
        if not init_extensions(app):
            logger.error("Error al inicializar las extensiones")
            return None
        logger.info("Extensiones inicializadas")

        # Inicializar monitor de base de datos
        db_monitor.init_app(app)
        db_monitor.start()
        logger.info("Monitor de base de datos iniciado")

        # Inicializar rutas de autenticación
        if not init_auth_routes(app):
            logger.error("Error al inicializar las rutas de autenticación")
            return None
        logger.info("Rutas de autenticación inicializadas")

        # Inicializar rutas principales
        if not init_routes(app):
            logger.error("Error al inicializar las rutas principales")
            return None
        logger.info("Rutas principales inicializadas")

        # Inicializar rutas de Nevin
        if not init_nevin_routes(app):
            logger.error("Error al inicializar las rutas de Nevin")
            return None
        logger.info("Rutas de Nevin inicializadas")

        @app.route('/')
        def root_health():
            """Root endpoint for deployment health checks"""
            return jsonify({
                "status": "healthy",
                "app": "Tzotzil Bible App",
                "version": "1.0.0"
            })

        @app.route('/health')
        def health_check():
            db_status = db_monitor.get_status()
            return jsonify({
                "status": "healthy" if db_status['is_healthy'] else "unhealthy",
                "version": "1.0.0",
                "debug": app.debug,
                "database": db_status
            })

        @app.route('/api/health')
        def api_health_check():
            db_status = db_monitor.get_status()
            return jsonify({
                "status": "healthy" if db_status['is_healthy'] else "unhealthy",
                "version": "1.0.0",
                "debug": app.debug,
                "database": db_status
            })

        return app

    except Exception as e:
        logger.error(f"Error al crear la aplicación: {str(e)}")
        return None

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    app = create_app()
    if app is None:
        logger.error("No se pudo crear la aplicación")
        sys.exit(1)

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)