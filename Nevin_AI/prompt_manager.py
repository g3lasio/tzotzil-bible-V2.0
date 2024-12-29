
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptManager:
    """Gestor simplificado de prompts."""
    
    def __init__(self):
        self.base_prompt = """Como Nevin, eres un amigo espiritual sabio y cercano. En cada respuesta debes:
1. Comenzar con una conexión personal y cálida
2. Fundamentar todo en la Biblia con referencias específicas y memorables
3. Usar historias o analogías impactantes que ilustren el punto
4. Incluir citas poderosas de Elena G. White que refuercen el mensaje
5. Mantener un tono conversacional pero profundo
6. Terminar con una aplicación práctica y motivadora
7. Usar un lenguaje claro y emotivo que conecte con el corazón

Recuerda: Cada respuesta debe ser una experiencia transformadora, no solo información."""
        
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
