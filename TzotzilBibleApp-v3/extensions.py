from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_babel import Babel
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from urllib.parse import urlparse
import os
import time
import logging
from sqlalchemy import text
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import shutil
import sqlite3
from datetime import datetime

load_dotenv()  # Añadir al inicio del archivo
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize extensions without binding to app yet
db = SQLAlchemy()
mail = Mail()
babel = Babel()
migrate = Migrate()
login_manager = LoginManager()


def verify_database_connection(db_session):
    """Verifica la conexión a la base de datos con timeout."""
    try:
        start_time = time.time()
        result = db_session.execute(text('SELECT 1'))
        response_time = time.time() - start_time

        if response_time > 5.0:
            logger.warning(
                f"Conexión a base de datos lenta: {response_time:.2f}s")

        row = result.fetchone()
        if row and row[0] == 1:
            logger.info("Verificación de conexión exitosa")
            return True, "Conexión exitosa"
        else:
            logger.error(
                "La consulta de verificación no retornó el resultado esperado")
            return False, "Error en la verificación de conexión"
    except Exception as e:
        error_msg = f"Error verificando conexión a la base de datos: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10))
def configure_database(app):
    """Configura la base de datos con opciones optimizadas y reintentos."""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL no está configurada")

        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://",
                                                1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'max_overflow': 2,
            'pool_recycle': 1800,
            'pool_pre_ping': True,
            'pool_timeout': 30
        }

        # Initialize the db with the app
        db.init_app(app)

        # Create tables if they don't exist
        with app.app_context():
            db.create_all()
            # Verify connection after initialization
            is_connected, _ = verify_database_connection(db.session)
            if not is_connected:
                raise Exception(
                    "No se pudo verificar la conexión después de la inicialización"
                )

        logger.info("Configuración de base de datos completada")
        return True
    except Exception as e:
        logger.error(f"Error configurando base de datos: {str(e)}")
        if db.session:
            db.session.remove()
        if hasattr(db, 'engine'):
            db.engine.dispose()
        return False


def configure_login_manager(app):
    """Configura el LoginManager con manejo de errores mejorado."""
    try:
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
        login_manager.login_message_category = 'info'

        from models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        logger.info("LoginManager configurado correctamente")
        return True
    except Exception as e:
        logger.error(f"Error configurando LoginManager: {str(e)}")
        return False


@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10))
def init_extensions(app):
    """Initialize Flask extensions with better error handling and retries"""
    try:
        logger.info("Iniciando proceso de inicialización de extensiones...")

        # 1. Configurar base de datos
        if not configure_database(app):
            raise Exception("Error en la configuración de la base de datos")

        # 2. Configurar login manager
        if not configure_login_manager(app):
            raise Exception("Error en la configuración del login manager")

        # 3. Inicializar extensiones en orden
        logger.info("Inicializando CORS...")
        CORS(app)

        logger.info("Inicializando Mail...")
        mail.init_app(app)

        logger.info("Inicializando Babel...")
        babel.init_app(app, locale_selector=get_locale)

        logger.info("Inicializando Migrate...")
        migrate.init_app(app, db)

        logger.info("Todas las extensiones inicializadas correctamente")
        return True

    except Exception as e:
        logger.error(f"Error crítico inicializando extensiones: {str(e)}")
        logger.error("Intentando limpieza de recursos...")
        try:
            if hasattr(db, 'session'):
                db.session.remove()
            if hasattr(db, 'engine'):
                db.engine.dispose()
        except Exception as cleanup_error:
            logger.error(f"Error durante limpieza: {str(cleanup_error)}")
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


def configure_database(app):
    """
    Sistema robusto de inicialización de base de datos SQLite con verificación 
    y manejo de errores avanzado.
    """
    try:
        # Configuración de rutas
        base_dir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(base_dir, 'instance', 'bible_app.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Configuración optimizada para SQLite
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

        with app.app_context():
            # Verificación específica para SQLite
            verification_query = """
                SELECT count(name) FROM sqlite_master 
                WHERE type='table' AND name IN ('bibleverse', 'users', 'favorite');
            """
            result = db.session.execute(text(verification_query))
            existing_tables = result.scalar()

            if existing_tables < 3:
                logger.info("Creando esquema de base de datos...")
                db.create_all()
                db.session.execute(text('PRAGMA integrity_check;'))
                db.session.execute(text('PRAGMA foreign_key_check;'))
                db.session.commit()

            # Verificación final
            test_query = "SELECT 1;"
            db.session.execute(text(test_query))
            db.session.commit()

            logger.info("Base de datos configurada exitosamente")
            return True

    except Exception as e:
        logger.error(f"Error en configuración de base de datos: {str(e)}")
        if hasattr(db, 'session'):
            db.session.remove()
        if hasattr(db, 'engine'):
            db.engine.dispose()
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