"""
BibleData - Módulo para búsqueda de versículos bíblicos con caché distribuido
"""
import logging
import json
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential
from models import BibleVerse, db
from cache_manager import cache_manager

# Configuración de logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BibleData:
    """Clase para gestionar búsquedas en la base de datos bíblica con caché distribuido."""

    def __init__(self):
        """Inicializa la clase BibleData con sistema de caché distribuido."""
        self.db = db
        self.cache = cache_manager
        logger.info("BibleData inicializado con sistema de caché distribuido")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda _: []
    )
    async def search_verses(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca versículos con caché distribuido.

        Args:
            query: Texto a buscar
            limit: Número máximo de resultados

        Returns:
            Lista de versículos encontrados
        """
        try:
            # Verificar caché
            cache_key = f"search:{query}:{limit}"
            cached_results = self.cache.get(cache_key)
            if cached_results:
                logger.info(f"Cache hit para búsqueda: {query}")
                return cached_results

            # Ejecutar búsqueda de forma asíncrona
            start_time = datetime.now()
            verses = await asyncio.to_thread(
                self._execute_search,
                query=query,
                limit=limit
            )
            query_time = (datetime.now() - start_time).total_seconds()

            results = []
            for verse in verses:
                result = {
                    'content': verse.spanish_text,
                    'content_tzotzil': verse.tzotzil_text,
                    'reference': f"{verse.book} {verse.chapter}:{verse.verse}",
                    'score': self._calculate_relevance_score(verse, query),
                    'type': 'bible'
                }
                results.append(result)

            # Guardar en caché distribuido
            self.cache.set(cache_key, results, ttl=900)  # 15 minutos TTL

            # Registrar métricas
            logger.info(
                "Búsqueda completada",
                extra={
                    'query': query,
                    'results_count': len(results),
                    'query_time': query_time,
                    'cache_status': 'miss'
                }
            )
            return results

        except Exception as e:
            logger.error(
                "Error en búsqueda de versículos",
                extra={
                    'error': str(e),
                    'query': query,
                    'limit': limit
                },
                exc_info=True
            )
            return []

    @cache_manager.cached(ttl=3600)
    def _execute_search(self, query: str, limit: int) -> List[BibleVerse]:
        """Ejecuta la búsqueda en la base de datos con caché."""
        try:
            # Construir consulta optimizada
            verses = BibleVerse.query.filter(
                (BibleVerse.spanish_text.ilike(f"%{query}%")) |
                (BibleVerse.tzotzil_text.ilike(f"%{query}%"))
            ).limit(limit).all()

            return verses

        except SQLAlchemyError as e:
            logger.error(
                "Error en base de datos",
                extra={
                    'error_type': type(e).__name__,
                    'error': str(e)
                },
                exc_info=True
            )
            return []
        except Exception as e:
            logger.error(
                "Error inesperado ejecutando búsqueda",
                extra={'error': str(e)},
                exc_info=True
            )
            return []

    def _calculate_relevance_score(self, verse: BibleVerse, query: str) -> float:
        """Calcula un score de relevancia para el versículo."""
        score = 1.0

        # Aumentar score si la coincidencia es exacta
        if query.lower() in verse.spanish_text.lower():
            score *= 1.2
        if query.lower() in verse.tzotzil_text.lower():
            score *= 1.2

        # Ajustar por longitud del versículo
        text_length = len(verse.spanish_text) + len(verse.tzotzil_text)
        length_factor = 1.0 / (1.0 + (text_length / 500))
        score *= (1.0 + length_factor)

        return min(score, 2.0)  # Limitar score máximo