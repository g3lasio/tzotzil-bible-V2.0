import os
import logging
from datetime import timedelta
from flask import render_template
from __init__ import create_app, db

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_app():
    """Inicializar y configurar la aplicación para producción"""
    try:
        app = create_app()
        
        # Configuración adicional de cookies
        app.config.update(
            PERMANENT_SESSION_LIFETIME=timedelta(days=31),
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax'
        )

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

        port = int(os.environ.get('PORT', 5000))
        return app, port

    except Exception as e:
        logger.error(f"Error en la inicialización de la aplicación: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        app, port = init_app()
        # Configuración del servidor
        app.run(
            host='0.0.0.0',  # Permitir acceso externo
            port=port,
            debug=False,
            ssl_context='adhoc'  # Para soporte HTTPS
        )
    except Exception as e:
        logger.error(f"Error fatal iniciando la aplicación: {str(e)}")
        raise