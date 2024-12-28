"""
Aplicación principal Flask con manejo de base de datos
"""
from flask import Flask, render_template, send_from_directory, redirect, url_for, session
import os
import logging
from datetime import timedelta
from extensions import init_extensions, db, login_manager
import sys

# Adding the current file directory to system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Crear y configurar la aplicación Flask"""
    try:
        logger.info("=== Iniciando proceso de arranque del servidor ===")
        logger.info("Creando aplicación Flask...")

        app = Flask(__name__)

        # Configuración básica
        app.config.update(SECRET_KEY=os.environ.get('FLASK_SECRET_KEY',
                                                    'default-secret-key'),
                          STATIC_URL_PATH='/static',
                          STATIC_FOLDER='static',
                          TEMPLATE_FOLDER='templates',
                          PERMANENT_SESSION_LIFETIME=timedelta(days=1))

        # Configuración optimizada de SQLite
        db_path = os.path.join(app.instance_path, 'bible_app.db')
        os.makedirs(app.instance_path, exist_ok=True)

        app.config.update(SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
                          SQLALCHEMY_TRACK_MODIFICATIONS=False,
                          SQLALCHEMY_ENGINE_OPTIONS={
                              'connect_args': {
                                  'timeout': 30,
                                  'check_same_thread': False
                              }
                          })

        logger.info("Verificando servicios críticos...")

        # Inicializar extensiones primero
        with app.app_context():
            if not init_extensions(app):
                logger.error("Error en servicios críticos")
                raise Exception("Error en servicios críticos")
        logger.info("Extensiones inicializadas correctamente")

        # Registrar blueprints después de inicializar extensiones
        from routes import routes
        from nevin_routes import nevin_bp
        from auth import auth

        app.register_blueprint(routes)
        app.register_blueprint(nevin_bp, url_prefix='/nevin')
        app.register_blueprint(auth, url_prefix='/auth')

        logger.info("Blueprints registrados correctamente")

        @app.route('/static/<path:filename>')
        def serve_static(filename):
            logger.info(f"Serving static file: {filename}")
            try:
                response = send_from_directory(app.static_folder, filename)
                logger.info(f"Static file {filename} served successfully")
                return response
            except Exception as e:
                logger.error(f"Error serving static file {filename}: {str(e)}")
                return "Error serving static file", 500

        @app.before_request
        def make_session_permanent():
            session.permanent = True

        @app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Error interno del servidor: {error}")
            db.session.rollback()
            return render_template('error.html',
                                   error="Error interno del servidor"), 500

        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('error.html',
                                   error="Página no encontrada"), 404

        logger.info("Aplicación Flask creada exitosamente")
        return app

    except Exception as e:
        logger.error(
            f"Error crítico durante la creación de la aplicación: {str(e)}",
            exc_info=True)
        raise


if __name__ == '__main__':
    try:
        app = create_app()
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Iniciando servidor en puerto {port}")
        logger.info(f"Starting Flask app in debug mode on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {str(e)}")
