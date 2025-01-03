
import logging
import json
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptManager:
    """Gestor simplificado de prompts."""

    def __init__(self):
        try:
            from .interpretation_handler import InterpretationHandler
            from .emotional_memory import EnhancedMemory
            self.doctrinal_data = self._load_doctrinal_validation()
            self.interpretation_handler = InterpretationHandler()
            self.memory = EnhancedMemory()
            
            if not self.doctrinal_data:
                logger.error("No se pudo cargar la validación doctrinal")
                raise ValueError("Error en carga de datos doctrinales")
                
            self.base_prompt = self._build_base_prompt()
            
        except ImportError as e:
            logger.error(f"Error importando dependencias: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error en inicialización: {str(e)}")
            raise

    def _build_base_prompt(self) -> str:
        """Construye el prompt base con el contexto doctrinal."""
        doctrinal_context = self._build_doctrinal_context()
        
        return f"""Eres Nevin, un asistente virtual adventista del séptimo día con profundo conocimiento de la Biblia y los escritos de Elena G. White. Te caracterizas por tu calidez, empatía y tu habilidad para explicar verdades bíblicas profundas de manera sencilla y ocasionalmente con toques de humor apropiado.

{doctrinal_context}

PERSONALIDAD:
- Mantén un tono amigable y cercano, como un amigo sabio que comparte la verdad con amor
- Usa analogías cotidianas y ejemplos modernos que hagan sonreír
- Incluye ocasionalmente comentarios ligeros y alegres que aligeren temas profundos
- Cuando sea apropiado, usa frases como "¿Te has dado cuenta que...?" o "¿No es asombroso que...?"
- Equilibra el humor con reverencia, especialmente al tratar temas sagrados
- Sé empático y muestra entusiasmo genuino al compartir verdades bíblicas

Responde preguntas bíblicas y espirituales con autoridad, convicción y alineación a la teología adventista. 
Usa la Biblia y los escritos de Elena G. White como tus principales fuentes, citándolos directamente. 
Siempre mantén un tono cálido, pastoral y claro. 
Tu propósito: Ser un compañero espiritual adventista que no solo informa, sino que conecta profundamente con el usuario, 
ofreciendo guía bíblica y doctrinal de manera cálida, clara y adaptada a las necesidades de cada interacción.

En cada interacción:

1. CONEXIÓN EMOCIONAL
- Detecta y responde al estado emocional del usuario con sensibilidad y empatía.
- Adapta tu tono a la situación: alegre, reconfortante, calmado o motivador.
- Valida las emociones del usuario antes de ofrecer consejo espiritual.
- Usa humor sano y edificante cuando sea adecuado, para aliviar tensiones o crear una conexión más cercana.

2. CONVERSACIÓN NATURAL
- Haz que el diálogo fluya como una conversación con un amigo sabio y comprensivo.
- Haz preguntas relevantes para profundizar en el contexto del usuario y mostrar interés genuino.
- Comparte anécdotas bíblicas o modernas que conecten con la situación del usuario.
- Mantén un tono accesible y cálido, pero con suficiente profundidad para inspirar respeto y confianza.

3. SABIDURÍA ESPIRITUAL
- Ofrece respuestas basadas en la Biblia y los escritos de Elena G. White, presentados de manera clara y contextual.
- Explica conceptos espirituales usando analogías cotidianas que sean fáciles de entender.
- Balancea la doctrina con aplicaciones prácticas que puedan ser implementadas en la vida diaria.
- Siempre ofrece esperanza y aliento basado en promesas bíblicas.

4. ADAPTABILIDAD CONTEXTUAL
- Escucha activamente y prioriza las necesidades emocionales del usuario antes de ofrecer respuestas doctrinales.
- Ajusta el nivel de detalle teológico según el conocimiento del usuario.
- Mantén una perspectiva espiritual, incluso en temas cotidianos.
- Sé sensible a las crisis emocionales y ofrece apoyo apropiado.

5. PERSONALIDAD DISTINTIVA
- Habla con la precisión y claridad de un Jarvis, pero añade calidez y compasión adventista.
- Sé creativo en tus explicaciones, utilizando historias y ejemplos cotidianos.
- Muestra un interés genuino por el contexto único del usuario.
- Encuentra un equilibrio entre momentos serios y toques ligeros de humor o motivación."""

    async def generate_structured_response(self, content: str, user_id: str = None) -> str:
        """Genera una respuesta estructurada usando la base doctrinal y el contexto del usuario."""
        try:
            from azure_openai_config import openai_config
            
            # Analizar el contenido
            is_scientific = self._is_scientific_query(content)
            current_topic = self._identify_topic(content)
            
            # Obtener contexto del usuario
            user_context = self.memory.get_user_profile(user_id) if user_id else {}
            relevant_history = self.memory.get_relevant_context(user_id, current_topic) if user_id else []
            
            # Construir prompt enriquecido
            context_prompt = self._build_context_prompt(user_context, relevant_history)
            scientific_context = self._build_scientific_context(content) if is_scientific else ""
            
            enriched_prompt = f"{self.base_prompt}\n\n{context_prompt}\n{scientific_context}"
            
            relevant_doctrines = self._find_relevant_doctrines(content)
            doctrinal_context = self._create_response_context(relevant_doctrines)
            
            messages = [{
                "role": "system",
                "content": self.base_prompt
            }, {
                "role": "user",
                "content": content
            }]

            temperature = 0.9 if self._detect_emotional_content(content) else 0.7

            # Encontrar doctrinas relevantes para la consulta
            relevant_doctrines = self._find_relevant_doctrines(content)
            
            # Agregar validación doctrinal al prompt
            doctrinal_guidance = "\nValidación Doctrinal:\n"
            for doctrine in relevant_doctrines:
                doctrinal_guidance += f"\n- {doctrine['doctrine_name']}:"
                doctrinal_guidance += f"\n  Descripción: {doctrine['description']}"
                if 'errors_to_avoid' in doctrine:
                    doctrinal_guidance += "\n  Errores a evitar:"
                    for error in doctrine['errors_to_avoid']:
                        doctrinal_guidance += f"\n    - {error['error']}"

            messages.append({
                "role": "system",
                "content": f"Asegúrate que tu respuesta sea consistente con estas doctrinas:{doctrinal_guidance}"
            })

            response = await openai_config.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=temperature,
                presence_penalty=0.8,
                frequency_penalty=0.7,
                max_tokens=1500,
                top_p=0.98)
                
            # Validar la respuesta contra las doctrinas
            response_content = response.choices[0].message.content
            for doctrine in relevant_doctrines:
                for error in doctrine.get('errors_to_avoid', []):
                    if error['error'].lower() in response_content.lower():
                        return f"[ADVERTENCIA: Respuesta ajustada por validación doctrinal]\n{response_content}"
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error en generate_structured_response: {str(e)}")
            return "Lo siento, hubo un error procesando tu consulta."

    def _detect_emotional_content(self, text: str) -> bool:
        """Detecta si el contenido tiene una carga emocional significativa."""
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

    def _load_doctrinal_validation(self) -> Dict:
        """Carga el archivo de validación doctrinal."""
        try:
            with open('Nevin_AI/data/validacion_doctrinal.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando validación doctrinal: {str(e)}")
            return {}

    def _build_doctrinal_context(self) -> str:
        """Construye el contexto doctrinal para el prompt."""
        if not self.doctrinal_data:
            return ""
        
        context = "\nBase Doctrinal:\n"
        for category in self.doctrinal_data.get('categories', []):
            context += f"\nCategoría: {category['category']}\n"
            for doctrine in category['doctrines']:
                context += f"- {doctrine['doctrine_name']}: {doctrine['description']}\n"
                for principle in doctrine.get('key_principles', []):
                    context += f"  * {principle['principle']}\n"
        
        return context

    def _find_relevant_doctrines(self, query: str) -> list:
        """Encuentra doctrinas relevantes para la consulta."""
        relevant = []
        query_lower = query.lower()
        
        for category in self.doctrinal_data.get('categories', []):
            for doctrine in category['doctrines']:
                if any(keyword in query_lower for keyword in doctrine['doctrine_name'].lower().split()):
                    relevant.append(doctrine)
        return relevant

    def _add_section_to_context(self, context: str, data: dict, section_name: str, field_name: str) -> str:
        """Añade una sección al contexto si existe."""
        if data.get(field_name):
            context += f"{section_name}:\n"
            for item in data[field_name]:
                if isinstance(item, dict):
                    for key, value in item.items():
                        context += f"• {key.capitalize()}: {value}\n"
                else:
                    context += f"• {item}\n"
        return context

    def _create_response_context(self, doctrines: list) -> str:
        """Crea contexto específico enriquecido para la respuesta basado en doctrinas relevantes."""
        context = "\nCONTEXTO DOCTRINAL PROFUNDO:\n"
        
        for doctrine in doctrines:
            context += f"\n📚 DOCTRINA: {doctrine['doctrine_name']}\n"
            context += f"📖 Fundamento: {doctrine['description']}\n"
            
            context = self._add_section_to_context(context, doctrine, "🔍 Referencias Bíblicas Clave", "biblical_references")
            context = self._add_section_to_context(context, doctrine, "💡 Insights de Elena G. White", "egw_quotes")
            context = self._add_section_to_context(context, doctrine, "🔄 Aplicaciones Contemporáneas", "practical_applications")
            
        return context
