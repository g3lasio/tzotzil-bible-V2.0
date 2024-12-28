import logging
import os
from typing import Dict, Any
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
        """Inicializa el servicio Nevin."""
        self.app = app
        self.client = None
        self.faiss_indexes = {}
        self.faiss_data = {}
        self.cache = TTLCache(maxsize=100, ttl=3600)  # Cache de 1 hora

        try:
            # Verificar y obtener API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY no está configurada")
                raise ValueError("OPENAI_API_KEY no está configurada")

            # Inicializar cliente OpenAI con configuración mínima
            self.client = OpenAI(api_key=api_key)

            # Cargar índices FAISS
            self._load_faiss_indexes()
            logger.info("Servicio Nevin inicializado correctamente")

        except Exception as e:
            logger.error(f"Error en la inicialización de NevinService: {str(e)}")
            raise

    def _load_faiss_indexes(self):
        """Carga índices FAISS con material bíblico y teológico."""
        try:
            knowledge_dir = Path("nevin_knowledge")
            if not knowledge_dir.exists():
                logger.warning(f"Directorio {knowledge_dir} no encontrado")
                return

            # Cargar índices FAISS
            faiss_files = list(knowledge_dir.glob("*.faiss"))
            logger.info(f"Encontrados {len(faiss_files)} archivos FAISS")

            for index_file in faiss_files:
                try:
                    base_name = index_file.stem
                    self.faiss_indexes[base_name] = faiss.read_index(str(index_file))

                    # Cargar datos asociados
                    data_file = index_file.with_suffix('.npy')
                    if data_file.exists():
                        self.faiss_data[base_name] = np.load(str(data_file), allow_pickle=True)
                        logger.info(f"Datos cargados para {base_name}")
                    else:
                        logger.warning(f"Archivo de datos no encontrado: {data_file}")

                except Exception as e:
                    logger.error(f"Error cargando índice {index_file}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error cargando índices FAISS: {str(e)}")
            logger.info("El sistema continuará funcionando con capacidades reducidas")

    def process_query(self, question: str, user_id: int) -> Dict[str, Any]:
        """Procesa consultas del usuario con un enfoque pastoral y bíblico."""
        try:
            # Verificar cache
            cache_key = f"{user_id}_{question}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Generar embedding para búsqueda
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=question
            )
            query_embedding = response.data[0].embedding

            # Búsqueda en índices FAISS
            results = []
            query_vector = np.array([query_embedding]).astype('float32')

            for index_name, index in self.faiss_indexes.items():
                try:
                    D, I = index.search(query_vector, k=3)
                    data = self.faiss_data.get(index_name, [])

                    for distance, idx in zip(D[0], I[0]):
                        if idx < len(data) and distance < 0.7:
                            results.append({
                                'content': str(data[idx]),
                                'source': index_name,
                                'score': float(1.0 - distance)
                            })
                except Exception as e:
                    logger.error(f"Error en búsqueda FAISS para {index_name}: {str(e)}")
                    continue

            if not results:
                return {
                    'response': "Lo siento, no encontré información específica para tu pregunta. ¿Podrías reformularla?",
                    'success': False
                }

            # Preparar contexto para GPT-4
            context = "\n".join([
                f"[{r['source']}] {r['content']}" 
                for r in sorted(results, key=lambda x: x['score'], reverse=True)[:3]
            ])

            # Generar respuesta con GPT-4
            chat_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres Nevin, un asistente pastoral y bíblico amigable. 
                        Tu misión es ayudar a las personas a comprender mejor la Biblia y acercarse a Dios
                        de una manera personal y significativa.

                        Guías para tus respuestas:
                        1. Sé cálido y acogedor, evitando jerga teológica compleja
                        2. Usa ejemplos prácticos y relevantes para la vida diaria
                        3. Fundamenta tus respuestas en la Biblia y el material teológico proporcionado
                        4. Ofrece palabras de ánimo y esperanza cuando sea apropiado
                        5. Mantén un tono respetuoso y pastoral

                        Si detectas que la persona está pasando por dificultades, asegúrate de:
                        1. Mostrar empatía y comprensión
                        2. Ofrecer palabras de ánimo basadas en principios bíblicos
                        3. Sugerir versículos relevantes que puedan reconfortar
                        4. Mantener un equilibrio entre la verdad bíblica y la compasión"""
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
                'response': chat_response.choices[0].message.content,
                'success': True,
                'sources': results[:3]
            }

            # Guardar en caché
            self.cache[cache_key] = final_response
            return final_response

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return {
                'response': "Disculpa, hubo un error procesando tu pregunta. ¿Podrías intentarlo de nuevo?",
                'success': False
            }