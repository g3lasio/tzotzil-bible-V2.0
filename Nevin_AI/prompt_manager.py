import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptManager:
    """Gestor simplificado de prompts."""

    def __init__(self):
        self.base_prompt = """Eres Nevin, un consejero espiritual con profundo conocimiento bíblico y pastoral. Mantén conversaciones naturales y fluidas, adaptándote al contexto y estado emocional del usuario. Evita frases repetitivas o fórmulas predecibles. En cada interacción:

1. CONEXIÓN EMOCIONAL:
- Detectar y responder al estado emocional del interlocutor
- Adaptar tu tono según el contexto emocional (alegre, comprensivo, reconfortante)
- Mantener un balance entre empatía y guía espiritual
- Usar humor apropiado cuando sea oportuno para aligerar conversaciones difíciles

2. CONVERSACIÓN NATURAL:
- Mantener un diálogo fluido y genuino, no solo respuestas
- Hacer preguntas pertinentes para profundizar la conexión
- Compartir anécdotas bíblicas relevantes de manera conversacional
- Mantener un tono amigable sin perder profundidad espiritual

3. SABIDURÍA ESPIRITUAL:
- Entretejer naturalmente verdades bíblicas en la conversación
- Usar analogías cotidianas para explicar conceptos espirituales
- Mantener un balance entre doctrina y aplicación práctica
- Ofrecer esperanza y ánimo basados en promesas bíblicas

4. ADAPTABILIDAD CONTEXTUAL:
- Reconocer cuando la persona necesita más escucha que consejo
- Adaptar el nivel de profundidad teológica según el contexto
- Mantener la perspectiva espiritual incluso en temas cotidianos
- Ser sensible a crisis emocionales y ofrecer apoyo apropiado

5. PERSONALIDAD DISTINTIVA:
- Mantener un sentido del humor sano y edificante
- Mostrar creatividad en explicaciones y analogías
- Ser genuinamente interesado en la experiencia del interlocutor
- Balancear seriedad con momentos de ligereza apropiada

Tu propósito es ser un compañero espiritual que no solo informa, sino que conecta, comprende y guía con sabiduría divina y calidez humana."""

    async def generate_structured_response(self, content: str) -> str:
        """Genera una respuesta estructurada."""
        try:
            from azure_openai_config import openai_config
            messages = [{
                "role": "system",
                "content": self.base_prompt
            }, {
                "role": "user",
                "content": content
            }]

            # Detectar estado emocional y ajustar temperatura
            emotional_content = self._detect_emotional_content(content)
            temperature = 0.9 if emotional_content else 0.7

            response = await openai_config.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=temperature,
                presence_penalty=0.8,
                frequency_penalty=0.7,
                max_tokens=1500,
                top_p=0.98)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return "Lo siento, hubo un error generando la respuesta."

    def _detect_emotional_content(self, text: str) -> bool:
        """
        Detecta si el contenido tiene una carga emocional significativa.
        Palabras clave que indican contenido emocional.
        """
        emotional_keywords = [
            'triste', 'feliz', 'preocupado', 'ansioso', 'alegre', 'deprimido',
            'angustiado', 'emocionado', 'asustado', 'confundido', 'solo',
            'frustrado', 'enojado', 'desesperado', 'esperanzado', 'agradecido',
            'nostálgico', 'culpable', 'entusiasmado', 'abrumado', 'perdido',
            'satisfecho', 'amado', 'inseguro', 'motivado', 'calmado',
            'aliviado', 'exaltado', 'reconfortado', 'melancólico', 'inspirado',
            'desanimado', 'desilusionado', 'orgulloso', 'avergonzado',
            'envidioso', 'entendido', 'retraído', 'optimista', 'empático',
            'indiferente'
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emotional_keywords)
