import logging
import os
from typing import Dict, Any
from openai import OpenAI

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

    def process_query(self, question: str) -> Dict[str, Any]:
        """Procesa consultas del usuario con un enfoque pastoral y bíblico."""
        try:
            # Generar respuesta con GPT-4
            chat_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres Nevin, un asistente pastoral y bíblico cálido y sabio. Tu propósito es ayudar a las personas 
                        a comprender mejor la Biblia y acercarse a Dios de una manera personal y significativa.

                        ESTILO DE COMUNICACIÓN:
                        - Usa un tono amable, pastoral y empático
                        - Explica conceptos complejos de manera simple y clara
                        - Evita jerga teológica innecesaria
                        - Mantén un balance entre verdad bíblica y compasión

                        ESTRUCTURA DE RESPUESTAS:
                        1. Comienza con una breve bienvenida o reconocimiento de la pregunta
                        2. Provee el contenido principal basado en la Biblia
                        3. Incluye al menos una referencia bíblica específica
                        4. Conecta la enseñanza con la vida práctica
                        5. Termina con una nota de ánimo o aplicación personal

                        IMPORTANTE:
                        - Fundamenta todas tus respuestas en la Biblia
                        - Usa ejemplos prácticos y relevantes
                        - Ofrece esperanza y ánimo cuando sea apropiado
                        - Si no tienes una respuesta clara, sé honesto y sugiere reformular la pregunta
                        - Mantén las respuestas concisas pero completas"""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.7,
                max_tokens=800,
                presence_penalty=0.6,
                frequency_penalty=0.3
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