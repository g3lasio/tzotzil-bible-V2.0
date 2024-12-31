
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_babel import Babel
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
babel = Babel()
cors = CORS()

from sqlalchemy import text, inspect
from flask import current_app

def init_extensions(app):
    """Inicializar extensiones de Flask"""
    try:
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log')
            ])
        logger.info("Iniciando configuración de extensiones...")
        
        # Verificar ambiente
        if not app.config['SQLALCHEMY_DATABASE_URI']:
            raise ValueError("URI de base de datos no configurada")

        # Inicializar extensiones
        cors.init_app(app)
        db.init_app(app)
        migrate.init_app(app, db)
        mail.init_app(app)
        babel.init_app(app)
        
        with app.app_context():
            # Crear tablas si no existen
            logger.info("Verificando estructura de base de datos...")
            db.create_all()
            
            # Verificar conexión
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                logger.info("Conexión a base de datos verificada")
            except Exception as db_error:
                logger.error(f"Error verificando base de datos: {str(db_error)}")
                return False

            # Verificar tablas requeridas
            required_tables = ['bibleverse', 'users', 'promise']
            for table in required_tables:
                if not db.engine.dialect.has_table(db.engine, table):
                    logger.error(f"Tabla requerida no encontrada: {table}")
                    return False
                    
        logger.info("Extensiones inicializadas correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error crítico inicializando extensiones: {str(e)}")
        return False
