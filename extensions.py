"""
Centralized extensions configuration
"""
import os
import time
import logging
from datetime import datetime
from flask import request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize extensions without binding to app yet
db = SQLAlchemy()
migrate = Migrate()

def configure_database(app):
    """Configura la base de datos con opciones optimizadas y fallback a SQLite."""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.warning("DATABASE_URL no configurada, usando SQLite")
            database_url = 'sqlite:///instance/bible_app.db'

        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10,
            'max_overflow': 2,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'pool_timeout': 30,
            'connect_args': {'connect_timeout': 10}
        }
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'max_overflow': 2,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'pool_timeout': 30
        }

        # Initialize the db with the app
        db.init_app(app)

        # Initialize migrations
        migrate.init_app(app, db)

        # Verify database connection
        with app.app_context():
            db.create_all()
            verify_database_connection(db.session)

        logger.info("Database configuration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}")
        if hasattr(db, 'session'):
            db.session.remove()
        if hasattr(db, 'engine'):
            db.engine.dispose()
        return False

def verify_database_connection(db_session):
    """Verifica la conexión a la base de datos con timeout."""
    try:
        start_time = time.time()
        result = db_session.execute(text('SELECT 1'))
        response_time = time.time() - start_time

        if response_time > 5.0:
            logger.warning(f"Slow database connection: {response_time:.2f}s")

        row = result.fetchone()
        if row and row[0] == 1:
            logger.info("Database connection verification successful")
            return True, "Connection successful"
        else:
            logger.error("Database verification query did not return expected result")
            return False, "Error in connection verification"
    except Exception as e:
        error_msg = f"Error verifying database connection: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def init_extensions(app):
    """Initialize Flask extensions"""
    try:
        logger.info("Iniciando inicialización de extensiones...")

        # Verificar configuración previa
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            raise ValueError("URI de base de datos no configurada")

        # Limpiar conexiones existentes
        if hasattr(db, 'session'):
            db.session.remove()
        if hasattr(db, 'engine'):
            db.engine.dispose()

        # Initialize database con retry
        for attempt in range(3):
            try:
                if configure_database(app):
                    break
                logger.warning(f"Intento {attempt + 1} de configuración de BD fallido")
                time.sleep(2)  # Esperar antes de reintentar
            except Exception as e:
                logger.error(f"Error en intento {attempt + 1}: {str(e)}")
                if attempt == 2:
                    raise

        logger.info("Extensions initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Error crítico inicializando extensiones: {str(e)}")
        if hasattr(db, 'session'):
            db.session.remove()
        return False

def get_locale():
    """Get locale for babel"""
    if request and 'language' in request.args:
        return request.args['language']
    return request.accept_languages.best_match(['en', 'es', 'tz'])

def diagnose_database(app):
    try:
        with app.app_context():
            # Verificación profunda del sistema
            system_checks = {
                'permissions':
                os.access(app.instance_path, os.W_OK),
                'disk_space':
                shutil.disk_usage(app.instance_path).free > 1024 * 1024 * 100,
                'sqlite_version':
                sqlite3.sqlite_version_info >= (3, 7, 0)
            }

            # Crear respaldo si existe base de datos
            if os.path.exists('instance/bible_app.db'):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                shutil.copy2('instance/bible_app.db',
                             f'instance/backup_{timestamp}.db')

            return system_checks
    except Exception as e:
        logger.error(f"Error en diagnóstico: {str(e)}")
        return None


def initialize_clean_database(app):
    try:
        with app.app_context():
            # Eliminar conexiones existentes
            db.session.remove()
            if hasattr(db, 'engine'):
                db.engine.dispose()

            # Configuración fresca
            db_path = os.path.join(app.instance_path, 'bible_app.db')
            if os.path.exists(db_path):
                os.remove(db_path)

            # Nueva configuración optimizada
            app.config.update({
                'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                'SQLALCHEMY_ENGINE_OPTIONS': {
                    'connect_args': {
                        'check_same_thread': False,
                        'timeout': 30
                    }
                }
            })

            db.init_app(app)
            db.create_all()

            # Verificación de integridad
            db.session.execute(text('PRAGMA integrity_check;'))
            db.session.execute(text('PRAGMA foreign_key_check;'))
            db.session.commit()

            return True
    except Exception as e:
        logger.error(f"Error en inicialización: {str(e)}")
        return False


def ensure_bible_integrity(app):
    """
    Sistema de verificación y protección de la integridad bíblica con múltiples 
    capas de seguridad y verificación.
    """
    try:
        with app.app_context():
            # Fase 1: Verificación de Integridad
            verse_verification = db.session.execute(
                text("SELECT COUNT(*), MIN(book), MAX(book) FROM bibleverse")
            ).fetchone()

            # Fase 2: Verificación de Contenido
            if verse_verification[0] > 0:
                logger.info(
                    f"Base de datos contiene {verse_verification[0]} versículos"
                )
                logger.info(
                    f"Rango de libros: {verse_verification[1]} a {verse_verification[2]}"
                )

                # Verificar integridad de los datos
                sample_verses = db.session.execute(
                    text("""
                        SELECT book, chapter, verse, tzotzil_text, spanish_text 
                        FROM bibleverse 
                        ORDER BY RANDOM() 
                        LIMIT 5
                    """)).fetchall()

                if all(verse[3] and verse[4] for verse in sample_verses):
                    logger.info("Verificación de contenido exitosa")

                    # Crear respaldo de seguridad
                    backup_path = os.path.join(
                        app.instance_path,
                        f'bible_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
                    )
                    with open(backup_path, 'wb') as backup_file:
                        for line in db.session.connection(
                        ).connection.iterdump():
                            backup_file.write(f'{line}\n'.encode('utf-8'))

                    return True
                else:
                    raise ValueError("Se detectaron versículos incompletos")
            else:
                logger.error("Base de datos sin contenido bíblico")
                raise ValueError("No se encontró contenido bíblico")

    except Exception as e:
        logger.error(f"Error crítico en verificación bíblica: {str(e)}")
        return False
import shutil
import sqlite3