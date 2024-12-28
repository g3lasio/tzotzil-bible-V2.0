"""
Aplicación principal Flask con manejo de base de datos
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """Crear y configurar la aplicación Flask"""
    logger.info("Iniciando creación de la aplicación Flask...")
    app = Flask(__name__)
    logger.info("Aplicación Flask creada exitosamente")

    # Configuración básica
    app.config.update(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'default-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'

    with app.app_context():
        # Importar y registrar blueprints
        from routes import routes
        from nevin_routes import nevin_bp
        from auth import auth

        app.register_blueprint(routes)
        app.register_blueprint(nevin_bp, url_prefix='/nevin')
        app.register_blueprint(auth, url_prefix='/auth')

        # Crear tablas
        try:
            db.create_all()
            logger.info("Base de datos inicializada correctamente")
            # Verificar conexión
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Conexión a la base de datos verificada exitosamente")
        except Exception as e:
            logger.error(f"Error al crear/verificar las tablas de la base de datos: {str(e)}")
            raise

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', error="Página no encontrada"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', error="Error interno del servidor"), 500

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)