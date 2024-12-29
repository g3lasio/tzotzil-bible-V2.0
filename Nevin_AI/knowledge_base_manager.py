"""
KnowledgeBaseManager - Módulo para búsqueda de contenido teológico usando FAISS con caché
"""
import logging
import numpy as np
import faiss
from faiss import IndexFlatL2
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from openai import OpenAI
from cachetools import TTLCache, LRUCache
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Gestiona búsquedas en la base de conocimientos teológicos usando FAISS."""

    def __init__(self, db=None, cache_ttl: int = 3600, faiss_index_path: str = "nevin_knowledge"):
        """
        Inicializa el gestor de base de conocimientos con caché.
        
        Args:
            db: Instancia de la base de datos SQLAlchemy
            cache_ttl: Tiempo de vida del caché en segundos (default: 1 hora)
            faiss_index_path: Ruta al directorio de índices FAISS
        """
        self.db = db
        self.client = OpenAI()
        self.faiss_indexes = {}
        self.faiss_data = {}
        self.faiss_index_path = faiss_index_path

        # Sistema de caché multinivel
        self.embeddings_cache = TTLCache(maxsize=1000,
                                         ttl=cache_ttl)  # Caché de embeddings
        self.results_cache = TTLCache(maxsize=500,
                                      ttl=cache_ttl)  # Caché de resultados
        self.frequent_queries = LRUCache(
            maxsize=100)  # Caché de consultas frecuentes

    def initialize(self) -> bool:
        """
        Inicializa el gestor de conocimientos y verifica la carga de índices FAISS.
        
        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            self._load_faiss_indexes()
            if not self.faiss_indexes:
                logger.error("No se pudieron cargar los índices FAISS")
                return False
                
            logger.info(f"FAISS inicializado exitosamente: {len(self.faiss_indexes)} índices cargados")
            return True
            
        except Exception as e:
            logger.error(f"Error en la inicialización de FAISS: {str(e)}")
            return False


        # Cola de procesamiento asíncrono
        self.processing_queue = asyncio.Queue()
        self.background_tasks = set()

        self._load_faiss_indexes()
        logger.info("KnowledgeBaseManager inicializado con sistema de caché")

    def _load_faiss_indexes(self):
        """Carga los índices FAISS desde el directorio de conocimiento."""
        try:
            knowledge_dir = Path("Nevin_AI/nevin_knowledge")
            logger.info(f"Inicializando índices FAISS desde: {knowledge_dir}")
            
            if not knowledge_dir.exists():
                logger.warning(f"Creando directorio {knowledge_dir}")
                knowledge_dir.mkdir(parents=True, exist_ok=True)
                return
                
            logger.info(f"Directorio FAISS encontrado: {knowledge_dir}")

            index_files = list(knowledge_dir.glob("*.faiss"))
            if not index_files:
                logger.info(
                    "No se encontraron índices FAISS. El sistema funcionará con capacidades reducidas."
                )
                return

            for index_file in index_files:
                try:
                    base_name = index_file.stem
                    index = faiss.read_index(str(index_file))

                    if not index.is_trained:
                        logger.warning(f"Índice {base_name} no está entrenado")
                        continue

                    self.faiss_indexes[base_name] = index

                    pkl_file = index_file.with_suffix('.pkl')
                    if pkl_file.exists():
                        with open(str(pkl_file), 'rb') as f:
                            self.faiss_data[base_name] = pickle.load(f)


                except Exception as e:
                    logger.warning(
                        f"Error cargando índice {index_file}: {str(e)}")
                    continue

        except Exception as e:
            logger.warning(f"Error cargando índices FAISS: {str(e)}")
            logger.info(
                "El sistema continuará funcionando con capacidades reducidas")

    async def _generate_embedding_async(self,
                                        text: str) -> Optional[List[float]]:
        """Genera embedding usando OpenAI de forma asíncrona con caché."""
        try:
            # Verificar caché de embeddings
            if text in self.embeddings_cache:
                logger.debug(f"Embedding encontrado en caché para: {text}")
                return self.embeddings_cache[text]

            # Generar embedding de forma asíncrona
            try:
                response = await asyncio.to_thread(
                    self.client.embeddings.create,
                    model="text-embedding-ada-002",
                    input=text)

                if not response.data:
                    return None

                embedding = response.data[0].embedding

                # Guardar en caché
                self.embeddings_cache[text] = embedding
                return embedding

            except Exception as e:
                logger.error(f"Error generando embedding asíncrono: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Error en _generate_embedding_async: {str(e)}")
            return None

    @lru_cache(maxsize=100)
    def _get_cached_search_results(
            self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Obtiene resultados cacheados de búsqueda."""
        return self.results_cache.get(cache_key)

    async def _process_search_queue(self):
        """Procesa la cola de búsquedas pendientes."""
        while True:
            try:
                query, future = await self.processing_queue.get()
                result = await self._execute_search(query)
                future.set_result(result)
            except Exception as e:
                logger.error(f"Error procesando cola de búsqueda: {str(e)}")
            finally:
                self.processing_queue.task_done()

    async def search_related_content(
            self,
            query: str,
            threshold: float = 0.7) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Busca contenido teológico relacionado usando FAISS con caché y procesamiento asíncrono.
        
        Args:
            query: Texto a buscar
            threshold: Umbral de similitud mínimo
            
        Returns:
            Tuple[List[Dict[str, Any]], bool]: (resultados, from_cache)
        """
        try:
            # Verificar caché de consultas frecuentes
            cache_key = f"{query}_{threshold}"
            if cache_key in self.results_cache:
                logger.info(f"Resultado encontrado en caché para: {query}")
                return self.results_cache[cache_key], True

            if not self.faiss_indexes:
                logger.info(
                    "No hay índices FAISS disponibles para la búsqueda")
                return [], False

            # Procesar embedding de forma asíncrona
            query_embedding = await self._generate_embedding_async(query)
            if not query_embedding:
                logger.warning("No se pudo generar embedding para la consulta")
                return [], False

            results = []
            query_vector = np.array(query_embedding).reshape(
                1, -1).astype('float32')

            for index_name, index in self.faiss_indexes.items():
                try:
                    D, I = index.search(query_vector, k=5)

                    if index_name in self.faiss_data:
                        data = self.faiss_data[index_name]
                        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
                            if idx < len(data) and distance < threshold:
                                score = 1.0 - (distance / 2.0)
                                results.append({
                                    'content': str(data[idx]),
                                    'source': index_name,
                                    'score': float(score),
                                    'type': 'theological'
                                })

                except Exception as e:
                    logger.warning(
                        f"Error buscando en índice {index_name}: {str(e)}")
                    continue

            sorted_results = sorted(results,
                                    key=lambda x: x['score'],
                                    reverse=True)
            # Guardar en caché antes de retornar
            self.results_cache[cache_key] = sorted_results
            return sorted_results, False

        except Exception as e:
            logger.warning(f"Error en búsqueda teológica: {str(e)}")
            return [], False