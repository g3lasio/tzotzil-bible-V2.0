
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import faiss
import numpy as np
from openai import OpenAI
from cachetools import TTLCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NevinService:
    """Servicio simplificado de Nevin."""
    
    def __init__(self, app=None):
        self.app = app
        self.client = OpenAI()
        self.faiss_indexes = {}
        self.faiss_data = {}
        self.cache = TTLCache(maxsize=1000, ttl=3600)
        self._load_faiss_indexes()

    def _load_faiss_indexes(self):
        """Carga índices FAISS."""
        try:
            knowledge_dir = Path("nevin_knowledge")
            if not knowledge_dir.exists():
                logger.warning(f"Directorio {knowledge_dir} no encontrado")
                return

            for index_file in knowledge_dir.glob("*.faiss"):
                try:
                    base_name = index_file.stem
                    self.faiss_indexes[base_name] = faiss.read_index(str(index_file))
                    data_file = index_file.with_suffix('.npy')
                    if data_file.exists():
                        self.faiss_data[base_name] = np.load(str(data_file))
                except Exception as e:
                    logger.warning(f"Error cargando índice {index_file}: {str(e)}")

        except Exception as e:
            logger.error(f"Error cargando índices: {str(e)}")

    async def process_query(self, question: str, user_id: int) -> Dict[str, Any]:
        """Procesa consultas de usuario."""
        try:
            cache_key = f"{user_id}_{question}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Generar embedding
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=question
            )
            query_embedding = response.data[0].embedding

            # Búsqueda en índices
            results = []
            query_vector = np.array(query_embedding).reshape(1, -1).astype('float32')

            for index_name, index in self.faiss_indexes.items():
                D, I = index.search(query_vector, k=5)
                data = self.faiss_data.get(index_name, [])
                
                for distance, idx in zip(D[0], I[0]):
                    if idx < len(data) and distance < 0.7:
                        results.append({
                            'content': str(data[idx]),
                            'score': float(1.0 - (distance / 2.0))
                        })

            # Generar respuesta
            if results:
                content = "\n".join([r['content'] for r in results[:3]])
                response = await self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un asistente teológico que proporciona respuestas basadas en la Biblia y escritos de Elena G. White."},
                        {"role": "user", "content": f"Responde esta pregunta usando este contenido como referencia:\nPregunta: {question}\nContenido: {content}"}
                    ]
                )
                
                final_response = {
                    'response': response.choices[0].message.content,
                    'success': True
                }
                self.cache[cache_key] = final_response
                return final_response

            return {
                'response': "Lo siento, no encontré información relevante para tu pregunta.",
                'success': False
            }

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return {
                'response': "Ocurrió un error procesando tu consulta.",
                'success': False
            }
