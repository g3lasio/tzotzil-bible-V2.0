import logging
import os
from typing import Dict, Any
import numpy as np
from openai import OpenAI

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NevinService:
    """Servicio simplificado de Nevin enfocado en respuestas bíblicas y pastorales."""

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

    def process_query(self, question: str) -> Dict[str, Any]:
        """Procesa consultas del usuario con un enfoque pastoral y bíblico."""
        try:
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
                        3. Fundamenta tus respuestas en la Biblia
                        4. Ofrece palabras de ánimo y esperanza cuando sea apropiado
                        5. Mantén un tono respetuoso y pastoral"""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )

            final_response = {
                'response': chat_response.choices[0].message.content,
                'success': True
            }

            return final_response

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return {
                'response': "Lo siento, tuve un problema procesando tu pregunta. ¿Podrías intentarlo de nuevo?",
                'success': False
            }