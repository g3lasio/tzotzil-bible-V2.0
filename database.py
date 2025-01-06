"""
DatabaseManager - Sistema simplificado de gestión de base de datos
"""
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from flask import g
from sqlalchemy import text, Column, DateTime
from extensions import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assumed User model -  needs to be adapted to your actual model
class User(db.Model):
    id = Column(db.Integer, primary_key=True)
    # ... other columns ...
    registered_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self._initialized = False
        self._session = None # Initialize session attribute

    def get_session(self):
        """Obtiene una sesión de base de datos con validación"""
        if self._session is None:
            self._session = db.session
        try:
            self._session.execute(text('SELECT 1'))
            return self._session
        except Exception as e:
            logger.error(f"Error de conexión a base de datos: {str(e)}")
            if self._session:
                self._session.rollback()
            self._session = db.session()
            return self._session
        except Exception as e:
            logger.error(f"Error de sesión de base de datos: {str(e)}")
            if self._session:
                self._session.rollback()
            self._session = db.session
            return self._session

    def get_books(self):
        """Obtener lista de libros ordenada con caché."""
        cache_key = 'bible_books_list'
        try:
            # Intentar obtener de la caché primero
            if hasattr(g, cache_key):
                return {
                    'success': True,
                    'data': getattr(g, cache_key),
                    'error': None,
                    'cached': True
                }

            session = self.get_session()
            result = session.execute(text("""
                SELECT DISTINCT book 
                FROM bibleverse 
                ORDER BY CASE 
                    WHEN book = ANY(ARRAY['Génesis','Éxodo','Levítico']) 
                    THEN 1 
                    ELSE 2 
                END, book
            """)).fetchall()
            
            books = [book[0] for book in result]
            # Guardar en caché
            setattr(g, cache_key, books)
            
            return {
                'success': True,
                'data': books,
                'error': None,
                'cached': False
            }
        except Exception as e:
            logger.error(f"Error obteniendo libros: {str(e)}")
            return {
                'success': False,
                'error': "Error de base de datos",
                'data': None
            }

    def get_verses(self, book: str, chapter: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene los versículos o capítulos de un libro"""
        try:
            session = self.get_session()
            if chapter is None:
                # Solo obtenemos los números de capítulo distintos
                query = text("""
                    SELECT DISTINCT CAST(chapter AS INTEGER) as chapter
                    FROM bibleverse 
                    WHERE book = :book 
                    ORDER BY chapter
                """)
                result = session.execute(query, {'book': book}).fetchall()
                chapters = [row.chapter for row in result] # Corrected line
                return {
                    'success': True,
                    'data': {'chapters': chapters},
                    'error': None
                }
            else:
                # Consulta para obtener versículos de un capítulo específico
                query = text("""
                    SELECT id, book, 
                           CAST(chapter AS INTEGER) as chapter, 
                           CAST(verse AS INTEGER) as verse, 
                           spanish_text, tzotzil_text 
                    FROM bibleverse 
                    WHERE book = :book AND CAST(chapter AS TEXT) = :chapter
                    ORDER BY verse
                """)
                result = session.execute(query, {'book': book, 'chapter': str(chapter)}).fetchall()
                verses = []
                for row in result:
                    verses.append({
                        'id': row[0],
                        'book': row[1],
                        'chapter': row[2],
                        'verse': row[3],
                        'spanish_text': row[4],
                        'tzotzil_text': row[5]
                    })
                return {
                    'success': True,
                    'data': {'verses': verses},
                    'error': None
                }
        except Exception as e:
            logger.error(f"Error getting verses: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }

    def check_health(self) -> Dict[str, Any]:
        """Verifica el estado de la conexión a la base de datos"""
        try:
            session = self.get_session()
            session.execute(text('SELECT 1')).scalar()
            return {
                'is_healthy': True,
                'error': None
            }
        except Exception as e:
            logger.error(f"Error en health check: {str(e)}")
            return {
                'is_healthy': False,
                'error': str(e)
            }

    def get_db():
        return db_manager.get_session()

def get_sorted_books():
    """Obtiene los libros ordenados según el orden bíblico"""
    try:
        books_result = db_manager.get_books()
        if not books_result['success']:
            return []
            
        books = books_result['data']
        
        # Ordenar según el orden bíblico definido en routes.py
        from routes import BIBLE_BOOKS_ORDER
        sorted_books = sorted(books, key=lambda x: BIBLE_BOOKS_ORDER.index(x) if x in BIBLE_BOOKS_ORDER else len(BIBLE_BOOKS_ORDER))
        return sorted_books
        
    except Exception as e:
        logger.error(f"Error ordenando libros: {str(e)}")
        return []

db_manager = DatabaseManager()

def get_db():
    return db_manager.get_session()