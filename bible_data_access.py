"""
BibleDataAccess - Sistema robusto de acceso a datos bíblicos con caché multinivel
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential
from extensions import db
from cache_manager import cache_manager
from database import db_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BibleDataAccess:
    """Gestor robusto de acceso a datos bíblicos con caché multinivel."""

    def __init__(self):
        """Inicializa el gestor de acceso a datos bíblicos."""
        self.cache = cache_manager
        self.db = db_manager
        logger.info("BibleDataAccess inicializado con sistema de caché multinivel")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_verse(self, book: str, chapter: int, verse: int) -> Dict[str, Any]:
        """
        Obtiene un versículo específico con caché.

        Args:
            book: Nombre del libro
            chapter: Número de capítulo
            verse: Número de versículo

        Returns:
            Diccionario con datos del versículo o error
        """
        cache_key = f"verse:{book}:{chapter}:{verse}"
        try:
            # Verificar caché
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit para versículo {book} {chapter}:{verse}")
                return cached_result

            start_time = datetime.now()
            result = self._fetch_verse(book, chapter, verse)
            query_time = (datetime.now() - start_time).total_seconds()

            if query_time > 0.5:
                logger.warning(f"Consulta lenta ({query_time:.2f}s) para {book} {chapter}:{verse}")

            # Guardar en caché si la consulta fue exitosa
            if result['success']:
                self.cache.set(cache_key, result, ttl=3600)

            return result

        except Exception as e:
            logger.error(f"Error obteniendo versículo: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': "Error interno del servidor",
                'data': None
            }

    def _fetch_verse(self, book: str, chapter: int, verse: int) -> Dict[str, Any]:
        """Obtiene un versículo de la base de datos."""
        try:
            session = self.db.get_session()
            query = """
                SELECT book, chapter, verse, spanish_text, tzotzil_text, version 
                FROM bibleverse 
                WHERE book = :book 
                AND chapter = :chapter 
                AND verse = :verse
            """
            result = session.execute(
                text(query),
                {'book': book, 'chapter': chapter, 'verse': verse}
            ).fetchone()

            if not result:
                return {
                    'success': False,
                    'error': "Versículo no encontrado",
                    'data': None
                }

            verse_data = {
                'book': result.book,
                'chapter': result.chapter,
                'verse': result.verse,
                'spanish_text': result.spanish_text,
                'tzotzil_text': result.tzotzil_text,
                'version': result.version
            }

            return {
                'success': True,
                'data': verse_data,
                'error': None
            }

        except SQLAlchemyError as e:
            logger.error(f"Error de base de datos: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': "Error de base de datos",
                'data': None
            }

    def get_chapter(self, book: str, chapter: int) -> Dict[str, Any]:
        """
        Obtiene un capítulo completo con caché.

        Args:
            book: Nombre del libro
            chapter: Número de capítulo

        Returns:
            Diccionario con versículos del capítulo o error
        """
        cache_key = f"chapter:{book}:{chapter}"
        try:
            # Verificar caché
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit para capítulo {book} {chapter}")
                return cached_result

            start_time = datetime.now()
            result = self._fetch_chapter(book, chapter)
            query_time = (datetime.now() - start_time).total_seconds()

            if query_time > 1.0:
                logger.warning(f"Consulta lenta ({query_time:.2f}s) para capítulo {book} {chapter}")

            # Guardar en caché si la consulta fue exitosa
            if result['success']:
                self.cache.set(cache_key, result, ttl=3600)

            return result

        except Exception as e:
            logger.error(f"Error obteniendo capítulo: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': "Error interno del servidor",
                'data': None
            }

    def _fetch_chapter(self, book: str, chapter: int) -> Dict[str, Any]:
        """Obtiene un capítulo de la base de datos."""
        try:
            session = self.db.get_session()
            query = """
                SELECT book, chapter, verse, spanish_text, tzotzil_text, version 
                FROM bibleverse 
                WHERE book = :book 
                AND chapter = :chapter 
                ORDER BY verse
            """
            results = session.execute(
                text(query),
                {'book': book, 'chapter': chapter}
            ).fetchall()

            if not results:
                return {
                    'success': False,
                    'error': "Capítulo no encontrado",
                    'data': None
                }

            verses = [{
                'book': row.book,
                'chapter': row.chapter,
                'verse': row.verse,
                'spanish_text': row.spanish_text,
                'tzotzil_text': row.tzotzil_text,
                'version': row.version
            } for row in results]

            return {
                'success': True,
                'data': verses,
                'error': None
            }

        except SQLAlchemyError as e:
            logger.error(f"Error de base de datos: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': "Error de base de datos",
                'data': None
            }

    def get_chapters(self, book: str) -> Dict[str, Any]:
        """
        Obtiene la lista de capítulos disponibles para un libro.

        Args:
            book: Nombre del libro

        Returns:
            Diccionario con lista de capítulos o error
        """
        cache_key = f"chapters:{book}"
        try:
            # Verificar caché
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit para capítulos de {book}")
                return cached_result

            start_time = datetime.now()
            session = self.db.get_session()

            query = """
                SELECT DISTINCT chapter 
                FROM bibleverse 
                WHERE book = :book 
                ORDER BY chapter
            """
            result = session.execute(text(query), {'book': book}).fetchall()
            query_time = (datetime.now() - start_time).total_seconds()

            if not result:
                return {
                    'success': False,
                    'error': f"No se encontraron capítulos para el libro {book}",
                    'data': None
                }

            chapters = [row[0] for row in result]

            response = {
                'success': True,
                'data': {'chapters': chapters},
                'error': None,
                'query_time': query_time
            }

            # Guardar en caché
            self.cache.set(cache_key, response, ttl=3600)

            if query_time > 0.5:
                logger.warning(f"Consulta lenta ({query_time:.2f}s) al obtener capítulos de {book}")

            return response

        except SQLAlchemyError as e:
            logger.error(f"Error de base de datos: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': "Error de base de datos",
                'data': None
            }
        except Exception as e:
            logger.error(f"Error obteniendo capítulos: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': "Error interno del servidor",
                'data': None
            }

    def get_verses(self, book, chapter=None):
        """Get verses with improved caching and error handling"""
        try:
            db = get_db() #Requires implementation of get_db() function
            if chapter:
                verses = db.execute(
                    'SELECT * FROM bibleverse WHERE book = ? AND chapter = ? ORDER BY verse',
                    (book, chapter)
                ).fetchall()
                return {
                    'success': True,
                    'data': {
                        'verses': [dict(verse) for verse in verses],
                        'total': len(verses)
                    }
                }
            else:
                chapters = db.execute(
                    'SELECT DISTINCT chapter FROM bibleverse WHERE book = ? ORDER BY chapter',
                    (book,)
                ).fetchall()
                return {
                    'success': True,
                    'data': {
                        'chapters': [dict(chapter)['chapter'] for chapter in chapters],
                        'total': len(chapters)
                    }
                }
        except Exception as e:
            logger.error(f"Database error in get_verses: {str(e)}")
            return {'success': False, 'error': str(e)}


def get_db():
    """Placeholder for database connection retrieval.  Replace with your actual DB connection."""
    # Implement your database connection logic here.  This is a placeholder.
    # Example using SQLAlchemy:
    # from sqlalchemy import create_engine
    # engine = create_engine('your_database_connection_string')
    # return engine.connect()
    raise NotImplementedError("get_db() function needs to be implemented")


# Instancia global del gestor de acceso a datos bíblicos
bible_data_access = BibleDataAccess()