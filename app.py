"""
Aplicación principal Flask con manejo de base de datos
"""
import os
import logging
from flask import Flask, render_template
from extensions import db, init_extensions

# Configuración básica de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Crear y configurar la aplicación Flask"""
    logger.info("Iniciando creación de la aplicación Flask...")
    app = Flask(__name__)

    # Configuración básica
    app.config.update(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'default-nevin-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///instance/bible_app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 5,
            'pool_timeout': 30
        }
    )

    logger.info("Configuración cargada exitosamente")

    # Inicializar extensiones
    try:
        if not init_extensions(app):
            logger.error("Error al inicializar las extensiones")
            raise RuntimeError("Failed to initialize extensions")
    except Exception as e:
        logger.error(f"Error crítico en inicialización: {str(e)}")
        raise

    # Registrar blueprints
    from routes import routes
    from nevin_routes import nevin_bp, init_nevin_service
    from auth import auth

    app.register_blueprint(routes)
    app.register_blueprint(nevin_bp, url_prefix='/nevin')
    app.register_blueprint(auth)

    # Inicializar servicio Nevin
    try:
        init_nevin_service(app)
    except Exception as e:
        logger.error(f"Error inicializando Nevin: {str(e)}")
        # Continue even if Nevin fails to initialize

    # Manejadores de error
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', error="Página no encontrada"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', error="Error interno del servidor"), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Error no manejado: {str(error)}")
        db.session.rollback()
        return render_template('error.html', error="Ha ocurrido un error inesperado"), 500

    logger.info("Aplicación Flask creada exitosamente")
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 3000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )