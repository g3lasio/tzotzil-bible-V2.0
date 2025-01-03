import asyncio
import logging
import os
from typing import Dict, Optional, Any, Union, List, Tuple
import numpy as np
import faiss
from pathlib import Path
from openai import OpenAI
from flask import current_app
from models import BibleVerse
from sqlalchemy import text
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NevinUtils:
    """Clase de utilidades para el asistente Nevin con búsqueda local y análisis teológico."""

    def __init__(self, app=None):
        """Inicializa OpenAI y carga los índices FAISS locales."""
        self.app = app
        self.client = None
        self.faiss_indexes = {}  # Almacena los índices FAISS por categoría
        self.faiss_data = {}     # Almacena los datos asociados a cada índice
        self.embeddings_cache = {}  # Cache para embeddings frecuentes

        # Inicializar componentes
        self._init_openai()
        self._load_faiss_indexes()
        logger.info("NevinUtils inicializado con éxito")

    def _init_openai(self):
        """Inicializa el cliente OpenAI con manejo de errores."""
        try:
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                logger.error("OPENAI_API_KEY no está configurada")
                return

            self.client = OpenAI(api_key=openai_key)
            logger.info("Cliente OpenAI inicializado correctamente")

        except Exception as e:
            logger.error(f"Error inicializando OpenAI client: {str(e)}")

    def _load_faiss_indexes(self):
        """Carga los índices FAISS y sus datos asociados desde la carpeta nevin_knowledge."""
        try:
            knowledge_paths = ['nevin_knowledge', 'Nevin_AI/nevin_knowledge']
            faiss_files = []
            for path in knowledge_paths:
                knowledge_dir = Path(path)
                if knowledge_dir.exists():
                    faiss_files.extend(knowledge_dir.glob("*.faiss"))

            logger.info(f"Encontrados {len(faiss_files)} archivos FAISS en {knowledge_paths}")

            for index_file in faiss_files:
                try:
                    # Extraer nombre base del archivo
                    base_name = index_file.stem

                    # Cargar índice FAISS
                    logger.info(f"Cargando índice: {index_file}")
                    index = faiss.read_index(str(index_file))

                    # Verificar que el índice esté entrenado
                    if not index.is_trained:
                        logger.warning(f"Índice {base_name} no está entrenado")
                        continue

                    self.faiss_indexes[base_name] = index

                    # Cargar datos asociados
                    data_file = index_file.with_suffix('.npy')
                    if data_file.exists():
                        self.faiss_data[base_name] = np.load(str(data_file), allow_pickle=True)
                        logger.info(f"Datos cargados para {base_name}: {len(self.faiss_data[base_name])} registros")
                    else:
                        logger.warning(f"No se encontró archivo de datos para {base_name}")

                except Exception as e:
                    logger.error(f"Error cargando índice {index_file}: {str(e)}")
                    continue

            if not self.faiss_indexes:
                logger.warning("No se cargaron índices FAISS. El sistema funcionará con capacidades reducidas.")
                return

            logger.info(f"Carga exitosa: {len(self.faiss_indexes)} índices FAISS")

        except Exception as e:
            logger.warning(f"Error cargando índices FAISS: {str(e)}")
            logger.info("El sistema continuará funcionando con capacidades reducidas")

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Genera embedding usando OpenAI de forma asíncrona."""
        try:
            if not self.client:
                raise ValueError("Cliente OpenAI no inicializado")

            # Verificar cache
            if text in self.embeddings_cache:
                return self.embeddings_cache[text]

            response = await asyncio.to_thread(
                lambda: self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
            )

            if not response.data or not response.data[0].embedding:
                raise ValueError("No se recibió embedding en la respuesta")

            embedding = response.data[0].embedding

            # Guardar en cache
            self.embeddings_cache[text] = embedding

            return embedding

        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            return None

    async def format_combined_results(self, combined_results: Dict[str, Any]) -> str:
        """Formatea los resultados combinados de búsqueda."""
        try:
            response = []

            # Formatear versículos bíblicos
            if combined_results.get('bible_verses'):
                response.append("📖 Versículos Bíblicos:")
                for verse in combined_results['bible_verses']:
                    response.append(f"__{verse['reference']}__ - {verse['content']}")
                    if verse.get('content_tzotzil'):
                        response.append(f"(Tzotzil: {verse['content_tzotzil']})")

            # Formatear contenido teológico
            if combined_results.get('theological_content'):
                response.append("\n📚 Comentarios Teológicos:")
                for comment in combined_results['theological_content']:
                    if comment.get('source'):
                        response.append(f"({comment['source']}) - {comment['content']}")
                    else:
                        response.append(f"{comment['content']}")

            return "\n".join(response)

        except Exception as e:
            logger.error(f"Error formateando resultados: {str(e)}")
            return "Lo siento, hubo un error al formatear los resultados."

    def search_bible(self, query: str, limit: int = 5) -> List[Dict]:
        """Busca versículos relevantes en la base de datos SQLite con logging detallado."""
        try:
            logger.info(f"Iniciando búsqueda bíblica para query: '{query}'")
            
            if not self.app:
                raise ValueError("App context no inicializado")
                
            with self.app.app_context():
                logger.info("Ejecutando consulta en base de datos...")
                # Realizar búsqueda por similitud semántica
                verses = BibleVerse.query.filter(
                    BibleVerse.spanish_text.ilike(f"%{query}%") |
                    BibleVerse.tzotzil_text.ilike(f"%{query}%")
                ).limit(limit).all()
                
                logger.info(f"Encontrados {len(verses)} versículos en la base de datos")
            
                results = []
                for verse in verses:
                    result = {
                        'content': verse.spanish_text,
                        'content_tzotzil': verse.tzotzil_text,
                        'reference': f"{verse.book} {verse.chapter}:{verse.verse}",
                        'score': 1.0,  # Score base para resultados directos
                        'type': 'bible'
                    }
                    results.append(result)
                    logger.debug(f"Agregado versículo: {result['reference']}")
            
                logger.info(f"Búsqueda bíblica completada exitosamente. Retornando {len(results)} resultados")
                return results
        
        except Exception as e:
            error_msg = f"Error en búsqueda bíblica: {str(e)}"
            logger.error(error_msg, exc_info=True)
            logger.error("Detalles del error:", {
                'query': query,
                'error_type': type(e).__name__,
                'app_context': bool(self.app)
            })
            return []

    def search_theological(self, query: str, threshold: float = 0.7) -> List[Dict]:
        """Realiza búsqueda en índices FAISS locales."""
        try:
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return []

            results = []
            query_vector = np.array(query_embedding).reshape(1, -1).astype('float32')

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
                    logger.error(f"Error buscando en índice {index_name}: {str(e)}")
                    continue

            return sorted(results, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            logger.error(f"Error en búsqueda teológica: {str(e)}")
            return []

    def generate_response(self, query: str, context: Dict[str, Any]) -> str:
        """Genera una respuesta estructurada usando GPT-4."""
        try:
            # Construir el prompt con el contexto
            prompt = self._build_prompt(query, context)

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": """Eres Nevin, un asistente teológico experto que proporciona respuestas 
                        profundas y elegantes, equilibrando claridad para principiantes con profundidad para expertos.
                        Usa las referencias proporcionadas para dar respuestas precisas y bien fundamentadas."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return "Lo siento, hubo un error al generar la respuesta. Por favor, intenta de nuevo."

    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Construye el prompt para GPT-4 con el contexto proporcionado."""
        prompt = f"""Como Nevin, responde a la siguiente pregunta teológica:
        
        Pregunta: {query}
        
        Contexto Bíblico:
        """
        # Añadir versículos bíblicos
        for verse in context.get('bible_verses', []):
            prompt += f"- {verse['reference']}: {verse['content']}\n"

        prompt += "\nContexto Teológico:\n"
        # Añadir comentarios teológicos
        for comment in context.get('theological_content', []):
            prompt += f"- Fuente ({comment['source']}): {comment['content']}\n"

        prompt += """
        Por favor, estructura tu respuesta así:
        1. Introducción Teológica (2-3 oraciones)
        2. Fundamento Bíblico (citando versículos relevantes)
        3. Explicación Teológica (para principiantes y expertos)
        4. Aplicación Práctica
        
        Formato para referencias:
        - Versículos: __Referencia__ - Texto
        - Comentarios: (Fuente) - Contenido
        """

        return prompt

    def process_query(self, query: str) -> Dict[str, Any]:
        """Procesa una consulta teológica completa con logging detallado."""
        try:
            logger.info(f"Iniciando procesamiento de consulta: '{query}'")
            
            # 1. Buscar versículos relevantes
            logger.info("Buscando versículos bíblicos relevantes...")
            bible_results = self.search_bible(query)
            logger.info(f"Encontrados {len(bible_results)} versículos relevantes")
            
            # 2. Buscar contenido teológico
            logger.info("Consultando base de conocimiento teológico (FAISS)...")
            theological_results = self.search_theological(query)
            logger.info(f"Encontrados {len(theological_results)} resultados teológicos")
            
            # 3. Preparar contexto para la respuesta
            logger.info("Preparando contexto para generación de respuesta...")
            context = {
                'bible_verses': bible_results,
                'theological_content': theological_results
            }
            
            # 4. Generar respuesta
            logger.info("Generando respuesta con GPT-4...")
            response = self.generate_response(query, context)
            logger.info("Respuesta generada exitosamente")
            
            result = {
                'success': True,
                'response': response,
                'sources': {
                    'bible': bible_results,
                    'theological': theological_results
                }
            }
            logger.info("Procesamiento completado exitosamente")
            return result
            
        except Exception as e:
            error_msg = f"Error procesando consulta: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'details': {
                    'error_type': type(e).__name__,
                    'error_location': 'process_query'
                }
            }
    async def format_combined_results(self, combined_results: Dict[str, Any]) -> str:
        """
        Formatea los resultados combinados de búsqueda de forma asíncrona.

        Args:
            combined_results: Diccionario con resultados de búsqueda

        Returns:
            Respuesta formateada
        """
        try:
            response = []

            # Formatear versículos bíblicos
            if combined_results.get('bible_verses'):
                response.append("📖 Versículos Bíblicos:")
                for verse in combined_results['bible_verses']:
                    response.append(f"__{verse['reference']}__ - {verse['content']}")
                    if verse.get('content_tzotzil'):
                        response.append(f"(Tzotzil: {verse['content_tzotzil']})")

            # Formatear contenido teológico
            if combined_results.get('theological_content'):
                response.append("\n📚 Comentarios Teológicos:")
                for comment in combined_results['theological_content']:
                    if comment.get('source'):
                        response.append(f"({comment['source']}) - {comment['content']}")
                    else:
                        response.append(f"{comment['content']}")

            return "\n".join(response)

        except Exception as e:
            logger.error(f"Error formateando resultados: {str(e)}")
            return "Lo siento, hubo un error al formatear los resultados."