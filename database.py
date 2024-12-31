"""
DatabaseManager - Sistema robusto de gestión de base de datos con verificación y recuperación automática
"""
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import time
import traceback
import os
from flask import g
from sqlalchemy import text, inspect
from extensions import db
from threading import Lock

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(),
              logging.FileHandler('app.log')])
logger = logging.getLogger(__name__)

def table_exists(engine, table_name):
    """Verifica si una tabla existe en la base de datos."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                """
                SELECT EXISTS (
                    SELECT FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename = :table_name
                )
                """
            ), {'table_name': table_name})
            return result.scalar()
    except Exception as e:
        logger.error(f"Error verificando existencia de tabla {table_name}: {str(e)}")
        return False

class DatabaseManager:
    """Gestor robusto de conexiones a base de datos con manejo de errores"""

    def __init__(self):
        """Inicializa el gestor de base de datos."""
        self._health_status = {
            'is_healthy': False,
            'last_check': None,
            'error': None,
            'reconnection_attempts': 0,
            'last_reconnection': None,
            'initialization_complete': False
        }
        self._max_reconnection_attempts = 5
        self._reconnection_delay = 2
        self._initialization_lock = Lock()
        self._session_lock = Lock()
        logger.info("DatabaseManager inicializado")

    def get_session(self):
        """Obtiene una sesión de base de datos con manejo de errores y reconexión automática"""
        with self._session_lock:
            try:
                if not hasattr(g, 'db_session'):
                    logger.info("Creando nueva sesión de base de datos...")
                    for attempt in range(3):
                        try:
                            g.db_session = db.session
                            g.db_session.execute(text('SELECT 1')).scalar()
                            logger.info("Nueva sesión de base de datos creada y verificada")
                            break
                        except Exception as e:
                            logger.error(f"Intento {attempt + 1} fallido: {str(e)}")
                            if hasattr(g, 'db_session'):
                                g.db_session.remove()
                            if attempt == 2:
                                raise
                            time.sleep(2)
                return g.db_session
            except Exception as e:
                logger.error(f"Error al obtener sesión de base de datos: {str(e)}")
                logger.error(traceback.format_exc())
                if hasattr(g, 'db_session'):
                    try:
                        g.db_session.remove()
                    except Exception:
                        pass
                    delattr(g, 'db_session')
                raise

    def initialize(self) -> Dict[str, Any]:
        """Inicializa la conexión a la base de datos de manera segura."""
        with self._initialization_lock:
            try:
                # Verificar estado actual
                if self._health_status['initialization_complete']:
                    # Validar conexión existente
                    try:
                        session = self.get_session()
                        session.execute(text('SELECT 1')).scalar()
                        logger.info("Conexión existente verificada")
                        return self._health_status
                    except Exception:
                        logger.warning("Reconectando base de datos...")
                        self._health_status['initialization_complete'] = False

                logger.info("Verificando integridad de la base de datos...")
                session = self.get_session()
                
                # Verificar la estructura y los datos
                result = session.execute(text("""
                    SELECT COUNT(*) as total_verses,
                           COUNT(DISTINCT book) as total_books
                    FROM bibleverse
                """)).fetchone()
                
                if result.total_verses < 31000 or result.total_books < 66:
                    logger.warning(f"Base de datos incompleta: {result.total_verses} versículos, {result.total_books} libros")
                    raise Exception("Base de datos incompleta")
                
                logger.info(f"Base de datos verificada: {result.total_verses} versículos, {result.total_books} libros")
                
                logger.info("Iniciando inicialización de la base de datos...")
                session = self.get_session()
                
                # Verificar conexión básica
                session.execute(text('SELECT 1')).scalar()
                logger.info("Conexión básica verificada")
                
                # Verificar existencia de tablas
                tables_result = session.execute(
                    text("""
                    SELECT name 
                    FROM pg_tables
                    WHERE schemaname = 'public' AND tablename = 'bibleverse'
                """)).fetchone()
                
                if not tables_result:
                    logger.error("Tabla 'bibleverse' no encontrada")
                    raise Exception("Tabla 'bibleverse' no encontrada")
                logger.info("Estructura de tablas verificada")
                
                self._health_status.update({
                    'is_healthy': True,
                    'last_check': datetime.utcnow(),
                    'error': None,
                    'initialization_complete': True
                })
                
                logger.info(
                    "Inicialización de base de datos completada exitosamente")
                return self._health_status
                
            except Exception as e:
                error_msg = f"Error en la inicialización de la base de datos: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                self._health_status.update({
                    'is_healthy': False,
                    'error': error_msg,
                    'last_check': datetime.utcnow()
                })
                return self._health_status
    
    def check_health(self) -> Dict[str, Any]:
        """Verifica el estado de salud de la base de datos"""
        try:
            session = self.get_session()
            start_time = time.time()
            
            # Verificar estructura de tablas críticas
            required_tables = ['bibleverse', 'users', 'promise', 'favorite']
            existing_tables = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).fetchall()
            
            existing_tables = [t[0] for t in existing_tables]
            missing_tables = set(required_tables) - set(existing_tables)
            
            if missing_tables:
                logger.error(f"Tablas faltantes: {missing_tables}")
                return {
                    'is_healthy': False,
                    'error': f'Faltan tablas requeridas: {missing_tables}',
                    'last_check': datetime.utcnow()
                }

            # Verificación básica
            session.execute(text('SELECT 1')).scalar()
            response_time = time.time() - start_time

            # Verificar tablas esenciales
            tables_check = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('bibleverse', 'users', 'promise')
            """)).fetchall()

            tables_exist = len(tables_check) == 3
            if not tables_exist:
                missing_tables = {'bibleverse', 'users', 'promise'} - {t[0] for t in tables_check}
                logger.warning(f"Tablas faltantes: {missing_tables}")

            health_status = {
                'is_healthy': True,
                'last_check': datetime.utcnow(),
                'error': None,
                'response_time': response_time,
                'tables_status': tables_exist
            }

            self._health_status.update(health_status)
            return self._health_status

        except Exception as e:
            error_msg = f"Error en health check: {str(e)}"
            logger.error(error_msg)
            self._health_status.update({
                'is_healthy': False,
                'last_check': datetime.utcnow(),
                'error': error_msg
            })
            return self._health_status

    def get_books(self):
        """Obtiene la lista de libros de la base de datos"""
        try:
            session = self.get_session()
            logger.info("Iniciando consulta para obtener libros...")

            if not table_exists(db.engine, "bibleverse"):
                raise Exception("La tabla 'bibleverse' no existe en la base de datos.")

            result = session.execute(text("""
                SELECT DISTINCT book
                FROM bibleverse
                ORDER BY book ASC
            """))

            books = [row[0] for row in result]
            logger.info(f"Libros obtenidos exitosamente: {len(books)} libros encontrados")

            return {'success': True, 'data': books, 'error': None}
        except Exception as e:
            error_msg = f"Error obteniendo libros: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'data': None, 'error': error_msg}

    def get_verses(self,
                   book: str,
                   chapter: Optional[int] = None,
                   verse: Optional[int] = None) -> Dict:
        """Obtiene versículos según los parámetros especificados"""
        try:
            session = self.get_session()

            if not table_exists(db.engine, 'bibleverse'):
                logger.error("La tabla 'bibleverse' no existe")
                return {
                    'success': False,
                    'data': None,
                    'error': "La tabla 'bibleverse' no existe"
                }

            if chapter is None:
                chapters_query = """
                    SELECT DISTINCT chapter 
                    FROM bibleverse 
                    WHERE book = :book 
                    ORDER BY chapter::integer
                """
                chapters_result = session.execute(text(chapters_query),
                                                {'book': book})
                chapters = [str(row[0]) for row in chapters_result]

                return {
                    'success': True,
                    'data': {
                        'book': book,
                        'chapters': chapters
                    },
                    'error': None
                }

            base_query = """
                SELECT id, book, chapter, verse, spanish_text, tzotzil_text 
                FROM bibleverse 
                WHERE book = :book
            """
            params = {'book': book}

            if chapter is not None:
                base_query += " AND chapter = :chapter"
                params['chapter'] = str(chapter)

            if verse is not None:
                base_query += " AND verse = :verse"
                params['verse'] = str(verse)

            base_query += " ORDER BY chapter::integer, verse::integer"

            result = session.execute(text(base_query), params)
            verses = []

            for row in result:
                verse_dict = dict(row._mapping)
                verses.append(verse_dict)

            logger.info(f"Versículos encontrados: {len(verses)}")

            return {
                'success': True,
                'data': {
                    'verses': verses,
                    'book': book,
                    'chapter': chapter if chapter else None
                },
                'error': None
            }

        except Exception as e:
            error_msg = f"Error obteniendo versículos: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {'success': False, 'data': None, 'error': error_msg}

    def backup_database(self) -> bool:
        """Realiza una copia de seguridad de la base de datos"""
        try:
            session = self.get_session()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'backup_{timestamp}.sql'
            backup_path = os.path.join('backups', backup_name)

            os.makedirs('backups', exist_ok=True)
            with open(backup_path, 'w') as backup_file:
                for line in session.connection().connection.iterdump():
                    backup_file.write(f'{line}\n')

            logger.info(
                f"Backup de la base de datos completado: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error realizando backup: {str(e)}")
            logger.error(traceback.format_exc())
            return False


# Instancia global del gestor
db_manager = DatabaseManager()

def get_verses(book: str,
               chapter: Optional[int] = None,
               verse: Optional[int] = None) -> Dict:
    """Obtiene versículos según los parámetros especificados"""
    return db_manager.get_verses(book, chapter, verse)

def get_books() -> Dict:
    """Obtiene la lista de libros de la base de datos"""
    return db_manager.get_books()

def backup_database() -> bool:
    """Realiza una copia de seguridad de la base de datos"""
    return db_manager.backup_database()

def get_db():
    """Obtiene una sesión de base de datos"""
    return db_manager.get_session()

# Orden bíblico de los libros
BIBLE_BOOKS_ORDER = [
    'Génesis', 'Éxodo', 'Levítico', 'Números', 'Deuteronomio', 'Josué',
    'Jueces', 'Rut', '1 Samuel', '2 Samuel', '1 Reyes', '2 Reyes',
    '1 Crónicas', '2 Crónicas', 'Esdras', 'Nehemías', 'Ester', 'Job', 'Salmos',
    'Proverbios', 'Eclesiastés', 'Cantares', 'Isaías', 'Jeremías',
    'Lamentaciones', 'Ezequiel', 'Daniel', 'Oseas', 'Joel', 'Amós', 'Abdías',
    'Jonás', 'Miqueas', 'Nahúm', 'Habacuc', 'Sofonías', 'Hageo', 'Zacarías',
    'Malaquías', 'Mateo', 'Marcos', 'Lucas', 'Juan', 'Hechos', 'Romanos',
    '1 Corintios', '2 Corintios', 'Gálatas', 'Efesios', 'Filipenses',
    'Colosenses', '1 Tesalonicenses', '2 Tesalonicenses', '1 Timoteo',
    '2 Timoteo', 'Tito', 'Filemón', 'Hebreos', 'Santiago', '1 Pedro',
    '2 Pedro', '1 Juan', '2 Juan', '3 Juan', 'Judas', 'Apocalipsis'
]

def get_sorted_books():
    """Obtiene lista de libros ordenados según el orden bíblico"""
    try:
        result = db_manager.get_books()
        if not result['success']:
            logger.error(f"Error obteniendo libros: {result['error']}")
            return []

        books = result['data']
        return sorted(books,
                     key=lambda x: BIBLE_BOOKS_ORDER.index(x)
                     if x in BIBLE_BOOKS_ORDER else 999)

    except Exception as e:
        logger.error(f"Error en get_sorted_books: {str(e)}")
        return []