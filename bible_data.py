
"""
BibleData - Módulo optimizado para acceso directo a base de datos SQLite con caché en memoria
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from models import BibleVerse, db
from cachetools import TTLCache
from database import with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BibleData:
    def __init__(self):
        """Inicializa el acceso a datos bíblicos con caché"""
        self.cache_ttl = 3600  # 1 hora
        self.verse_cache = TTLCache(maxsize=1000, ttl=self.cache_ttl)
        self.book_cache = TTLCache(maxsize=100, ttl=self.cache_ttl)
        self.verify_database()

    @with_retry(max_retries=3)
    def verify_database(self) -> None:
        """Verifica que la base de datos tenga datos con reintentos y protección"""
        try:
            # Verificar cantidad total de versículos
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT book) as total_books,
                    COUNT(DISTINCT chapter) as total_chapters
                FROM bibleverse
            """)).fetchone()
            
            total_verses = result[0]
            total_books = result[1]
            total_chapters = result[2]
            
            logger.info(f"Estadísticas de base de datos:")
            logger.info(f"- Total versículos: {total_verses}")
            logger.info(f"- Total libros: {total_books}")
            logger.info(f"- Total capítulos: {total_chapters}")
            
            # Verificar integridad de datos
            if total_verses < 31000:  # Debería haber aproximadamente 31,105 versículos
                logger.error(f"¡ALERTA! Posible pérdida de datos. Solo hay {total_verses} versículos")
                logger.error("La base de datos puede estar incompleta o corrupta")
                raise Exception(f"Base de datos incompleta: {total_verses} versículos encontrados")
                
            if total_books < 66:  # La Biblia tiene 66 libros
                logger.error(f"¡ALERTA! Faltan libros. Solo hay {total_books} libros")
                raise Exception(f"Faltan libros en la base de datos: {total_books} encontrados")
            
            logger.info("Verificación de integridad completada exitosamente")
            
        except Exception as e:
            logger.error(f"Error crítico verificando base de datos: {str(e)}", exc_info=True)
            raise

    @with_retry(max_retries=3)
    def get_chapter_verses(self, book: str, chapter: int) -> List[Dict[str, Any]]:
        """Obtiene versículos de un capítulo específico con caché y verificación de integridad"""
        cache_key = f"{book}-{chapter}"
        
        # Intentar obtener del caché primero
        if cache_key in self.verse_cache:
            cached_verses = self.verse_cache[cache_key]
            # Verificar integridad de datos en caché
            if not cached_verses:
                logger.warning(f"Caché corrupto detectado para {cache_key}, recargando de base de datos")
                self.verse_cache.pop(cache_key, None)
            else:
                logger.info(f"Retornando {len(cached_verses)} versículos desde caché para {cache_key}")
                return cached_verses

        try:
            # Query optimizada usando SQLAlchemy text()
            result = db.session.execute(
                text("""
                    SELECT id, book, chapter, verse, tzotzil_text, spanish_text
                    FROM bibleverse
                    WHERE book = :book AND chapter = :chapter
                    ORDER BY verse
                """),
                {"book": book, "chapter": chapter}
            )
            
            verses = [{
                "id": f"{book}-{chapter}-{row.verse}",
                "verse": row.verse,
                "tzotzil_text": row.tzotzil_text,
                "spanish_text": row.spanish_text
            } for row in result]
            
            # Guardar en caché
            self.verse_cache[cache_key] = verses
            logger.info(f"Versículos almacenados en caché para {cache_key}")
            
            return verses
            
        except Exception as e:
            logger.error(f"Error obteniendo versículos: {str(e)}", exc_info=True)
            return []

    @with_retry(max_retries=3)
    def get_books(self) -> List[str]:
        """Obtiene lista de libros disponibles con caché"""
        cache_key = 'all_books'
        
        # Intentar obtener del caché primero
        if cache_key in self.book_cache:
            logger.info("Retornando libros desde caché")
            return self.book_cache[cache_key]

        try:
            result = db.session.execute(
                text("""
                    SELECT DISTINCT book 
                    FROM bibleverse 
                    ORDER BY book
                """)
            )
            books = [row[0] for row in result]
            
            # Guardar en caché
            self.book_cache[cache_key] = books
            logger.info("Lista de libros almacenada en caché")
            
            return books
            
        except Exception as e:
            logger.error(f"Error obteniendo libros: {str(e)}", exc_info=True)
            return []

    def get_verse(self, book: str, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """Obtiene un versículo específico con caché"""
        cache_key = f"{book}-{chapter}-{verse}"
        
        if cache_key in self.verse_cache:
            logger.info(f"Retornando versículo desde caché: {cache_key}")
            return self.verse_cache[cache_key]
            
        try:
            result = db.session.execute(
                text("""
                    SELECT id, book, chapter, verse, tzotzil_text, spanish_text
                    FROM bibleverse
                    WHERE book = :book AND chapter = :chapter AND verse = :verse
                """),
                {"book": book, "chapter": chapter, "verse": verse}
            ).first()
            
            if result:
                verse_data = {
                    "id": f"{book}-{chapter}-{verse}",
                    "verse": verse,
                    "tzotzil_text": result.tzotzil_text,
                    "spanish_text": result.spanish_text
                }
                self.verse_cache[cache_key] = verse_data
                return verse_data
                
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo versículo específico: {str(e)}", exc_info=True)
            return None
