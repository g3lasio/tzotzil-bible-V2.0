
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptManager:
    """Gestor simplificado de prompts."""
    
    def __init__(self):
        self.base_prompt = """Como Nevin, siempre debes:
1. Fundamentar respuestas en la Biblia
2. Mantener enfoque cristocéntrico
3. Usar escritos de Elena G. White como apoyo
4. Ser claro y accesible
5. Inspirar acercamiento a Cristo"""
        
    async def generate_structured_response(self, content: str) -> str:
        """Genera una respuesta estructurada."""
        try:
            from azure_openai_config import openai_config
            response = await openai_config.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.base_prompt},
                    {"role": "user", "content": content}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return "Lo siento, hubo un error generando la respuesta."
