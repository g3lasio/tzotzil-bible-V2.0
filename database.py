"""
DatabaseManager - Sistema simplificado de gestión de base de datos
"""
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from flask import g
from sqlalchemy import text
from extensions import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._initialized = False
        
    def get_session(self):
        """Obtiene una sesión de base de datos"""
        if not hasattr(g, 'db_session'):
            g.db_session = db.session
        return g.db_session

    def get_books(self):
        """Obtiene la lista de libros de la base de datos"""
        try:
            session = self.get_session()
            query = text('''
                SELECT DISTINCT book, MIN(id) as order_id
                FROM bibleverse 
                GROUP BY book
                ORDER BY order_id
            ''')
            result = session.execute(query).fetchall()
            return {
                'success': True,
                'data': [book[0] for book in result],
                'error': None
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
                query = text("""
                    SELECT DISTINCT chapter 
                    FROM bibleverse 
                    WHERE book = :book 
                    ORDER BY chapter
                """)
                result = session.execute(query, {'book': book}).fetchall()
                return {
                    'success': True,
                    'data': {'chapters': [row[0] for row in result]},
                    'error': None
                }
            else:
                query = text("""
                    SELECT verse, tzotzil_text, spanish_text 
                    FROM bibleverse 
                    WHERE book = :book AND chapter = :chapter 
                    ORDER BY verse
                """)
                result = session.execute(query, {'book': book, 'chapter': chapter}).fetchall()
                return {
                    'success': True,
                    'data': {'verses': [{'verse': row[0], 'tzotzil': row[1], 'spanish': row[2]} 
                            for row in result]},
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