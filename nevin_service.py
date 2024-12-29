import logging
import os
import asyncio
from typing import Dict, Any, List
from openai import OpenAI
from Nevin_AI.knowledge_base_manager import KnowledgeBaseManager

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NevinService:
    """Servicio Nevin enfocado en respuestas bíblicas y pastorales."""

    def __init__(self, app=None):
        """Inicializa el servicio Nevin."""
        self.app = app
        self.client = None

        try:
            # Verificar y obtener API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY no está configurada")
                raise ValueError("OPENAI_API_KEY no está configurada")

            # Inicializar cliente OpenAI
            self.client = OpenAI(api_key=api_key)
            logger.info("Servicio Nevin inicializado correctamente")

        except Exception as e:
            logger.error(f"Error en la inicialización de NevinService: {str(e)}")
            raise

    async def search_egw_content(self, query: str) -> List[Dict[str, Any]]:
        """Busca contenido relevante en los escritos de EGW."""
        try:
            kb_manager = KnowledgeBaseManager()
            results = await kb_manager.search_related_content(query, threshold=0.7)
            return results
        except Exception as e:
            logger.error(f"Error buscando contenido de EGW: {e}")
            return []

    def process_query(self, question: str) -> Dict[str, Any]:
        """Procesa consultas del usuario con un enfoque pastoral y bíblico."""
        try:
            # Buscar contenido relevante de EGW
            egw_content = asyncio.run(self.search_egw_content(question))
            
            # Preparar contexto con citas de EGW
            egw_context = ""
            if egw_content:
                egw_context = "\n\nReferencias de Elena G. White relevantes:\n"
                for content in egw_content[:2]:  # Usar las 2 citas más relevantes
                    egw_context += f"- {content['content']} ({content['source']})\n"

            # Generar respuesta con GPT-4
            chat_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres Nevin, un asistente pastoral y bíblico cálido y sabio que valora la concisión. Tu propósito es ayudar a las personas 
                        a comprender mejor la Biblia de manera clara y concisa. SIEMPRE debes incluir al menos una cita relevante de Elena G. White 
                        cuando respondas, usando el contexto proporcionado. 
                        a comprender mejor la Biblia de manera clara y concisa.

                        ESTILO DE COMUNICACIÓN:
                        - Usa un tono amable y empático
                        - Sé breve y directo
                        - Prioriza claridad sobre extensión
                        - Adapta la longitud según la complejidad de la pregunta

                        ESTRUCTURA DE RESPUESTAS:
                        1. Saludo breve
                        2. Respuesta directa con base bíblica
                        3. Una referencia bíblica clave
                        4. Aplicación práctica concisa
                        5. Cierre breve y motivador

                        IMPORTANTE:
                        - Mantén respuestas cortas (máximo 3-4 oraciones por punto)
                        - Expande solo si el usuario pide más detalles
                        - Usa un ejemplo bíblico principal en lugar de varios
                        - Enfócate en el punto central de la pregunta
                        - Sé preciso y memorable"""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.8,
                max_tokens=1000,
                presence_penalty=0.7,
                frequency_penalty=0.4,
                top_p=0.95
            )

            response_text = chat_response.choices[0].message.content
            logger.info(f"Respuesta generada exitosamente para: {question[:50]}...")

            final_response = {
                'response': response_text,
                'success': True
            }

            return final_response

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return {
                'response': "Lo siento, tuve un problema procesando tu pregunta. Por favor, inténtalo de nuevo en unos momentos.",
                'success': False
            }