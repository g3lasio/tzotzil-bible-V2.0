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

    def __init__(self, egw_dir: str = "nevin_knowledge", other_dir: str = "other_authors"):
        """
        Inicializa el gestor de la base de conocimientos.
        
        Args:
            egw_dir: Directorio que contiene los archivos FAISS de EGW
            other_dir: Directorio que contiene los archivos FAISS de otros autores
        """
        self.egw_dir = Path(egw_dir)
        self.other_dir = Path(other_dir)
        self.client = OpenAI()
        self.faiss_indexes = {'egw': {}, 'other': {}}
        self.faiss_data = {'egw': {}, 'other': {}}
        self.faiss_index_path = {'egw': self.egw_dir, 'other': self.other_dir}

        # Sistema de caché multinivel
        self.embeddings_cache = TTLCache(maxsize=1000,
                                         ttl=3600)  # Caché de embeddings
        self.results_cache = TTLCache(maxsize=500,
                                      ttl=3600)  # Caché de resultados
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
            if not self.faiss_indexes['egw'] and not self.faiss_indexes['other']:
                logger.error("No se pudieron cargar los índices FAISS")
                return False
                
            logger.info(f"FAISS inicializado exitosamente: {len(self.faiss_indexes['egw'])} índices EGW y {len(self.faiss_indexes['other'])} índices de otros autores cargados")
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
            for source, directory in self.faiss_index_path.items():
                logger.info(f"Inicializando índices FAISS desde: {directory}")
                
                if not directory.exists():
                    logger.warning(f"Creando directorio {directory}")
                    directory.mkdir(parents=True, exist_ok=True)
                    continue
                    
                logger.info(f"Directorio FAISS encontrado: {directory}")

                index_files = list(directory.glob("*.faiss"))
                if not index_files:
                    logger.info(
                        f"No se encontraron índices FAISS para {source}. El sistema funcionará con capacidades reducidas."
                    )
                    continue

                for index_file in index_files:
                    try:
                        base_name = index_file.stem
                        index = faiss.read_index(str(index_file))

                        if not index.is_trained:
                            logger.warning(f"Índice {base_name} para {source} no está entrenado")
                            continue

                        self.faiss_indexes[source][base_name] = index

                        pkl_file = index_file.with_suffix('.pkl')
                        if pkl_file.exists():
                            with open(str(pkl_file), 'rb') as f:
                                self.faiss_data[source][base_name] = pickle.load(f)


                    except Exception as e:
                        logger.warning(
                            f"Error cargando índice {index_file} para {source}: {str(e)}")
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

    def search_knowledge_base(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca en la base de conocimientos de forma síncrona."""
        try:
            if not self.faiss_indexes['egw'] and not self.faiss_indexes['other']:
                logger.info("No hay índices FAISS disponibles")
                return []

            # Generar embedding de forma síncrona
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=query)
            
            query_embedding = response.data[0].embedding
            query_vector = np.array(query_embedding).reshape(1, -1).astype('float32')

            results = []
            for source, indexes in self.faiss_indexes.items():
                for index_name, index in indexes.items():
                    try:
                        D, I = index.search(query_vector, top_k)
                        if index_name in self.faiss_data[source]:
                            data = self.faiss_data[source][index_name]
                            for i, (distance, idx) in enumerate(zip(D[0], I[0])):
                                if idx < len(data):
                                    score = 1.0 - (distance / 2.0)
                                    results.append({
                                        'content': str(data[idx]),
                                        'metadata': {'source': source, 'index': index_name},
                                        'score': float(score)
                                    })
                    except Exception as e:
                        logger.warning(f"Error en índice {index_name} de {source}: {str(e)}")
                        continue

            return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]

        except Exception as e:
            logger.error(f"Error en search_knowledge_base: {str(e)}")
            return []

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

            if not self.faiss_indexes['egw'] and not self.faiss_indexes['other']:
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

            for source, indexes in self.faiss_indexes.items():
                for index_name, index in indexes.items():
                    try:
                        D, I = index.search(query_vector, k=5)

                        if index_name in self.faiss_data[source]:
                            data = self.faiss_data[source][index_name]
                            for i, (distance, idx) in enumerate(zip(D[0], I[0])):
                                if idx < len(data) and distance < threshold:
                                    score = 1.0 - (distance / 2.0)
                                    results.append({
                                        'content': str(data[idx]),
                                        'source': source,
                                        'index': index_name,
                                        'score': float(score),
                                        'type': 'theological'
                                    })

                    except Exception as e:
                        logger.warning(
                            f"Error buscando en índice {index_name} de {source}: {str(e)}")
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