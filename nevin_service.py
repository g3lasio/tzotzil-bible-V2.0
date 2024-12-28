import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path
import faiss
import numpy as np
from openai import OpenAI
from cachetools import TTLCache

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NevinService:
    """Servicio simplificado de Nevin enfocado en respuestas bíblicas y pastorales."""

    def __init__(self, app=None):
        """Inicializa el servicio Nevin con manejo robusto de errores."""
        self.app = app
        self.faiss_indexes = {}
        self.faiss_data = {}
        self.cache = TTLCache(maxsize=100, ttl=3600)  # Cache de 1 hora

        try:
            # Inicializar OpenAI
            self.client = OpenAI()
            logger.info("Cliente OpenAI inicializado correctamente")

            # Cargar índices FAISS
            self._load_faiss_indexes()
            logger.info("Inicialización de NevinService completada con éxito")
        except Exception as e:
            logger.error(f"Error en la inicialización de NevinService: {str(e)}")
            raise

    def _load_faiss_indexes(self):
        """Carga índices FAISS con material bíblico y teológico."""
        try:
            knowledge_dir = Path("nevin_knowledge")
            if not knowledge_dir.exists():
                logger.error(f"Directorio de conocimiento no encontrado: {knowledge_dir}")
                raise FileNotFoundError(f"Directorio no encontrado: {knowledge_dir}")

            logger.info(f"Buscando índices FAISS en: {knowledge_dir}")
            faiss_files = list(knowledge_dir.glob("*.faiss"))
            logger.info(f"Encontrados {len(faiss_files)} archivos FAISS")

            for index_file in faiss_files:
                try:
                    base_name = index_file.stem
                    logger.info(f"Cargando índice: {index_file}")

                    # Cargar índice FAISS
                    self.faiss_indexes[base_name] = faiss.read_index(str(index_file))

                    # Cargar datos asociados
                    data_file = index_file.with_suffix('.npy')
                    if data_file.exists():
                        self.faiss_data[base_name] = np.load(str(data_file), allow_pickle=True)
                        logger.info(f"Datos cargados para {base_name}: {len(self.faiss_data[base_name])} registros")
                    else:
                        logger.warning(f"Archivo de datos no encontrado: {data_file}")

                except Exception as e:
                    logger.error(f"Error cargando índice {index_file}: {str(e)}")
                    continue

            if not self.faiss_indexes:
                logger.error("No se pudieron cargar índices FAISS")
                raise ValueError("No se pudieron cargar índices FAISS")

            logger.info(f"Carga exitosa de {len(self.faiss_indexes)} índices FAISS")

        except Exception as e:
            logger.error(f"Error en la carga de índices FAISS: {str(e)}")
            raise

    async def process_query(self, question: str, user_id: int) -> Dict[str, Any]:
        """Procesa consultas del usuario con un enfoque pastoral y bíblico."""
        try:
            # Verificar caché
            cache_key = f"{user_id}_{question}"
            if cache_key in self.cache:
                logger.info("Respuesta encontrada en caché")
                return self.cache[cache_key]

            logger.info(f"Procesando nueva consulta para usuario {user_id}")

            # Generar embedding para la pregunta
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=question
                )
                query_embedding = response.data[0].embedding
                logger.info("Embedding generado exitosamente")
            except Exception as e:
                logger.error(f"Error generando embedding: {str(e)}")
                raise

            # Búsqueda en índices FAISS
            results = []
            query_vector = np.array([query_embedding]).astype('float32')

            # Buscar en todos los índices disponibles
            for index_name, index in self.faiss_indexes.items():
                try:
                    D, I = index.search(query_vector, k=3)  # Top 3 resultados más relevantes
                    data = self.faiss_data.get(index_name, [])

                    for distance, idx in zip(D[0], I[0]):
                        if idx < len(data) and distance < 0.7:  # Umbral de relevancia
                            results.append({
                                'content': str(data[idx]),
                                'source': index_name,
                                'score': float(1.0 - distance)
                            })
                except Exception as e:
                    logger.error(f"Error en búsqueda FAISS para índice {index_name}: {str(e)}")
                    continue

            # Si no hay resultados relevantes
            if not results:
                logger.info("No se encontraron resultados relevantes para la consulta")
                return {
                    'response': "Lo siento, no encontré información específica para tu pregunta en mi base de conocimientos bíblicos. ¿Podrías reformularla o ser más específico?",
                    'success': False
                }

            # Preparar contexto para GPT-4
            context = "\n".join([
                f"[{r['source']}] {r['content']}" 
                for r in sorted(results, key=lambda x: x['score'], reverse=True)[:3]
            ])

            logger.info("Generando respuesta con GPT-4")
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": """Eres Nevin, un asistente pastoral y bíblico amigable. 
                            Tu propósito es ayudar a las personas a comprender mejor la Biblia y acercarse a Dios.
                            Usa un tono cálido y acogedor, evitando jerga teológica compleja.
                            Si detectas que la persona está pasando por dificultades, ofrece palabras de ánimo
                            basadas en principios bíblicos."""
                        },
                        {
                            "role": "user",
                            "content": f"Pregunta: {question}\n\nContexto bíblico y teológico:\n{context}"
                        }
                    ],
                    temperature=0.7,
                    max_tokens=800
                )

                final_response = {
                    'response': response.choices[0].message.content,
                    'success': True,
                    'sources': results[:3]  # Incluir las fuentes más relevantes
                }

                # Guardar en caché
                self.cache[cache_key] = final_response
                logger.info("Respuesta generada y guardada en caché exitosamente")
                return final_response

            except Exception as e:
                logger.error(f"Error generando respuesta con GPT-4: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return {
                'response': "Disculpa, hubo un error procesando tu pregunta. ¿Podrías intentarlo de nuevo?",
                'success': False,
                'error': str(e)
            }