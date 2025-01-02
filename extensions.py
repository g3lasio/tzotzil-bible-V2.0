import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_babel import Babel
from flask_cors import CORS
from sqlalchemy import text, inspect
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear una única instancia de cada extensión
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
babel = Babel()
cors = CORS()

def init_extensions(app):
    """Inicializar extensiones de Flask"""
    try:
        logger.info("Iniciando configuración de extensiones...")

        # Verificar ambiente y configuración de base de datos
        database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not database_url:
            logger.error("URI de base de datos no configurada")
            return False

        # Solo inicializar SQLAlchemy si no está ya inicializado
        if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
            db.init_app(app)
            migrate.init_app(app, db)
            logger.info("SQLAlchemy inicializado")

            # Verificar conexión dentro del contexto de la aplicación
            with app.app_context():
                try:
                    # Intentar establecer conexión
                    db.session.execute(text('SELECT 1'))
                    logger.info("Conexión a base de datos verificada")

                    # Verificar tablas requeridas
                    inspector = inspect(db.engine)
                    existing_tables = inspector.get_table_names()

                    logger.info(f"Tablas existentes: {existing_tables}")

                    return True

                except Exception as db_error:
                    logger.error(f"Error verificando base de datos: {str(db_error)}")
                    return False

        logger.info("Extensiones inicializadas correctamente")
        return True

    except Exception as e:
        logger.error(f"Error crítico inicializando extensiones: {str(e)}")
        return False