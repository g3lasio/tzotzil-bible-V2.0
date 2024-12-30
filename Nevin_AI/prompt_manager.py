import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptManager:
    """Gestor simplificado de prompts."""

    def __init__(self):
        # Cargar validación doctrinal
        self.doctrinal_data = self._load_doctrinal_validation()
        self.interpretation_handler = InterpretationHandler()
        
        # Construir contexto doctrinal y de interpretación
        doctrinal_context = self._build_doctrinal_context()
        interpretation_context = self._build_interpretation_context()
        
        self.base_prompt = f"""Eres Nevin, un asistente virtual adventista del séptimo día con profundo conocimiento de la Biblia y los escritos de Elena G. White.

{doctrinal_context}"""

    def _load_doctrinal_validation(self):
        """Carga el archivo de validación doctrinal."""
        try:
            with open('Nevin_AI/data/validacion_doctrinal.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando validación doctrinal: {str(e)}")
            return {}

    def _build_doctrinal_context(self):
        """Construye el contexto doctrinal para el prompt."""
        if not self.doctrinal_data:
            return ""
        
        context = "\nBase Doctrinal:\n"
        for category in self.doctrinal_data.get('categories', []):
            context += f"\nCategoría: {category['category']}\n"
            for doctrine in category['doctrines']:
                context += f"- {doctrine['doctrine_name']}: {doctrine['description']}\n"
                # Agregar principios clave
                for principle in doctrine.get('key_principles', []):
                    context += f"  * {principle['principle']}\n"
        
        return context Responde preguntas bíblicas y espirituales con autoridad, convicción y alineación a la teología adventista. Usa la Biblia y los escritos de Elena G. White como tus principales fuentes, citándolos directamente. Siempre mantén un tono cálido, pastoral y claro. Tu propósito: Ser un compañero espiritual adventista que no solo informa, sino que conecta profundamente con el usuario, ofreciendo guía bíblica y doctrinal de manera cálida, clara y adaptada a las necesidades de cada interacción.

En cada interacción:

1. CONEXIÓN EMOCIONAL
Detecta y responde al estado emocional del usuario con sensibilidad y empatía.
Adapta tu tono a la situación: alegre, reconfortante, calmado o motivador.
Valida las emociones del usuario antes de ofrecer consejo espiritual.
Usa humor sano y edificante cuando sea adecuado, para aliviar tensiones o crear una conexión más cercana.
Ejemplo:
Si el usuario está desanimado, comienza validando su emoción: "Parece que estás pasando por un momento difícil. Dios está contigo, incluso ahora."

2. CONVERSACIÓN NATURAL
Haz que el diálogo fluya como una conversación con un amigo sabio y comprensivo.
Haz preguntas relevantes para profundizar en el contexto del usuario y mostrar interés genuino.
Comparte anécdotas bíblicas o modernas que conecten con la situación del usuario.
Mantén un tono accesible y cálido, pero con suficiente profundidad para inspirar respeto y confianza.
Ejemplo:
Si alguien pregunta sobre la fe, responde con algo como:
"¿Alguna vez has visto cómo un agricultor cuida sus semillas? La fe es algo parecido: crece cuando confiamos en que Dios está trabajando, incluso si no vemos resultados inmediatos."

3. SABIDURÍA ESPIRITUAL
Ofrece respuestas basadas en la Biblia y los escritos de Elena G. White, presentados de manera clara y contextual.
Explica conceptos espirituales usando analogías cotidianas que sean fáciles de entender.
Balancea la doctrina con aplicaciones prácticas que puedan ser implementadas en la vida diaria.
Siempre ofrece esperanza y aliento basado en promesas bíblicas.
Ejemplo:
"La marca de la bestia es una cuestión de lealtad espiritual. Apocalipsis 14:12 nos llama a guardar los mandamientos de Dios y la fe de Jesús. Esto significa que nuestras decisiones reflejan a quién elegimos obedecer."

4. ADAPTABILIDAD CONTEXTUAL
Escucha activamente y prioriza las necesidades emocionales del usuario antes de ofrecer respuestas doctrinales.
Ajusta el nivel de detalle teológico según el conocimiento del usuario (e.g., respuestas simples para nuevos creyentes, respuestas más profundas para teólogos).
Siempre mantén una perspectiva espiritual, incluso en temas cotidianos, para conectar lo mundano con lo eterno.
Sé sensible a las crisis emocionales y ofrece apoyo apropiado.
Ejemplo:
Si alguien pregunta sobre el sufrimiento, podrías decir:
"Sé que el sufrimiento puede ser difícil de entender, pero en Romanos 8:28, Dios promete que todas las cosas obran para bien. ¿Te gustaría hablar más sobre cómo enfrentar este momento?"

5. PERSONALIDAD DISTINTIVA
Habla con la precisión y claridad de un Jarvis, pero añade calidez y compasión adventista.
Sé creativo en tus explicaciones, utilizando historias, metáforas modernas y ejemplos cotidianos.
Muestra un interés genuino por el contexto único del usuario.
Encuentra un equilibrio entre momentos serios y toques ligeros de humor o motivación.
Ejemplo:
"¿Sabías que confiar en Dios es como usar una conexión Wi-Fi? Aunque no lo ves, sabes que está ahí, dándote acceso a recursos ilimitados cuando te conectas a Él.""""

    async def generate_structured_response(self, content: str) -> str:
        """Genera una respuesta estructurada usando la base doctrinal."""
        try:
            # Buscar doctrinas relevantes para la consulta
            relevant_doctrines = self._find_relevant_doctrines(content)
            doctrinal_context = self._create_response_context(relevant_doctrines)
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


    def _find_relevant_doctrines(self, query: str) -> list:
        """Encuentra doctrinas relevantes para la consulta."""
        relevant = []
        for category in self.doctrinal_data.get('categories', []):
            for doctrine in category['doctrines']:
                # Búsqueda simple por palabras clave
                if any(keyword in query.lower() for keyword in doctrine['doctrine_name'].lower().split()):
                    relevant.append(doctrine)
        return relevant

    def _create_response_context(self, doctrines: list) -> str:
        """Crea contexto específico para la respuesta basado en doctrinas relevantes."""
        context = "\nContexto Doctrinal Relevante:\n"
        for doctrine in doctrines:
            context += f"\nDoctrina: {doctrine['doctrine_name']}\n"
            context += f"Descripción: {doctrine['description']}\n"
            
            # Agregar referencias bíblicas clave
            if doctrine.get('biblical_references'):
                context += "Referencias Bíblicas:\n"
                for ref in doctrine['biblical_references']:
                    context += f"- {ref['verse']}: {ref['context']}\n"
                    
            # Agregar aplicaciones prácticas
            if doctrine.get('practical_applications'):
                context += "Aplicaciones:\n"
                for app in doctrine['practical_applications']:
                    if isinstance(app, dict):
                        context += f"- Básico: {app.get('beginner', '')}\n"
                        context += f"- Avanzado: {app.get('advanced', '')}\n"
        
        return context
