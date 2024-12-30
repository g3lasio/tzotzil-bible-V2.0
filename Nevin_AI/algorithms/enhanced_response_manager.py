"""
Módulo mejorado para el manejo de respuestas de Nevin integrado con Tzotzil Bible App
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from Nevin_AI.prompts import PromptManager

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EnhancedResponseManager:
    """Clase para enriquecer las respuestas generadas por Nevin."""

    def __init__(self, interpretation_engine):
        """
        Inicializa el gestor de respuestas con un motor de interpretación.
        :param interpretation_engine: Instancia de InterpretationEngine.
        """
        self.interpretation_engine = interpretation_engine
        self.prompt_manager = PromptManager()
        self.conversation_context = {
            "emotional_state": "neutral",
            "conversation_depth": 0,
            "last_bible_refs": [],
            "last_egw_refs": []
        }

    def generate_response(self, query: str, text_type: str, lang: str = 'es') -> Dict[str, Any]:
        """
        Genera una respuesta enriquecida y formateada.
        :param query: Consulta del usuario
        :param text_type: Tipo de texto identificado
        :param lang: Idioma de respuesta ('es' para español, 'tzo' para tzotzil)
        :return: Respuesta enriquecida con formato estructurado
        """
        try:
            # Analizar estado emocional y contexto
            emotional_state = self._analyze_emotional_state(query)
            self.conversation_context["emotional_state"] = emotional_state
            self.conversation_context["conversation_depth"] += 1

            # Obtener prompt enriquecido
            enriched_prompt = self.prompt_manager.get_chat_prompt(
                query,
                emotional_state=emotional_state,
                conversation_depth=self.conversation_context["conversation_depth"]
            )

            # Generar interpretación base con contexto enriquecido
            interpretation = self.interpretation_engine.interpret(
                query,
                text_type,
                context=enriched_prompt
            )

            if "error" not in interpretation:
                # Adaptar el formato según el contexto emocional y el idioma
                response = self._format_response_by_context(
                    interpretation,
                    emotional_state,
                    lang
                )

                # Actualizar contexto con la nueva interacción
                self.prompt_manager.update_context({
                    "query": query,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })

                return {
                    "response": response,
                    "success": True,
                    "context": self._prepare_context_data()
                }
            else:
                return {
                    "response": self._generate_empathetic_error_response(lang),
                    "success": False,
                    "context": self._prepare_context_data()
                }

        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return {
                "response": self._generate_empathetic_error_response(lang),
                "success": False,
                "context": self._prepare_context_data()
            }

    def _format_bible_reference(self, reference: str, content: str, tzotzil_content: Optional[str] = None) -> str:
        """Formatea una referencia bíblica con estilo mejorado."""
        return self.prompt_manager.format_response(
            f'[BIBLE]{content}\n{tzotzil_content if tzotzil_content else ""}\n{reference}[/BIBLE]',
            include_references=True
        )

    def _format_egw_quote(self, quote: str, source: str) -> str:
        """Formatea una cita de Elena G. White con estilo mejorado."""
        return self.prompt_manager.format_response(
            f'[EGW]{quote}\n- {source}[/EGW]',
            include_references=True
        )

    def _format_response_by_context(self, interpretation: Dict[str, Any], emotional_state: str, lang: str) -> str:
        """
        Formatea la respuesta según el contexto emocional y el idioma.
        """
        # Personalizar introducción según estado emocional
        intro_phrases = {
            "es": {
                "alegre": "¡Qué hermoso es compartir tu alegría! ",
                "triste": "Comprendo tu dolor y estoy aquí para acompañarte. ",
                "preocupado": "Entiendo tu preocupación. Permíteme compartir algo que puede ayudarte. ",
                "confundido": "Es normal sentirse así. Vamos a explorar esto juntos. ",
                "enojado": "Veo que esta situación te afecta profundamente. ",
                "esperanzado": "Tu fe es inspiradora. ",
                "neutral": "Gracias por compartir conmigo. "
            },
            "tzo": {
                # Agregar frases en tzotzil según sea necesario
                "neutral": "Colaval ti la aval scotol. "
            }
        }

        selected_lang = "tzo" if lang == "tzo" else "es"
        intro = intro_phrases[selected_lang].get(
            emotional_state, 
            intro_phrases[selected_lang]["neutral"]
        )

        # Construir respuesta estructurada
        if self.conversation_context["conversation_depth"] > 1:
            # Para conversaciones más profundas, usar un formato más personal
            insight = self._generate_personal_insight(interpretation)
            meditation_points = self._generate_meditation_points(interpretation)

            response_parts = [
                intro,
                self._format_box("Perspectiva", insight),
                self._format_box("Reflexión", interpretation.get('principios', 'Sin principios disponibles')),
                "<strong>Para meditar:</strong>",
                self._format_bullets(meditation_points)
            ]

            # Agregar referencias bíblicas si existen
            if bible_refs := interpretation.get('bible_refs', []):
                response_parts.extend([
                    "<h3>Referencias Bíblicas:</h3>",
                    *[self._format_bible_reference(ref['reference'], ref['content'], ref.get('tzotzil_content'))
                      for ref in bible_refs]
                ])

            # Agregar citas de EGW si existen
            if egw_quotes := interpretation.get('egw_quotes', []):
                response_parts.extend([
                    "<h3>Escritos de Elena G. White:</h3>",
                    *[self._format_egw_quote(quote['content'], quote['source'])
                      for quote in egw_quotes]
                ])

        else:
            # Para primeras interacciones, mantener un formato más estructurado
            response_parts = [
                intro,
                "<h3>Base Bíblica:</h3>",
                interpretation.get('principios', 'Sin principios disponibles'),
                "<h3>Explicación:</h3>",
                self._generate_explanation(interpretation),
                "<h3>Aplicación Práctica:</h3>",
                self._generate_practical_application(interpretation)
            ]

        return "\n\n".join(response_parts)

    def _format_box(self, title: str, content: str) -> str:
        """Formatea un cuadro de contenido con estilo."""
        return f'<div class="nevin-box"><strong>{title}:</strong><br>{content}</div>'

    def _format_bullets(self, items: List[str]) -> str:
        """Formatea una lista de elementos con viñetas."""
        return "\n".join([f'<div class="nevin-bullet">{item}</div>' for item in items])

    def _prepare_context_data(self) -> Dict[str, Any]:
        """Prepara los datos de contexto para la siguiente interacción."""
        return {
            "timestamp": datetime.now().isoformat(),
            "conversation_depth": self.conversation_context["conversation_depth"],
            "emotional_state": self.conversation_context["emotional_state"],
            "last_bible_refs": self.conversation_context["last_bible_refs"],
            "last_egw_refs": self.conversation_context["last_egw_refs"]
        }

    def _analyze_emotional_state(self, text: str) -> str:
        """Analiza el estado emocional del texto."""
        emotional_indicators = {
            "alegre": ["feliz", "alegre", "contento", "gozo", "dichoso"],
            "triste": ["triste", "deprimido", "dolor", "pena", "sufriendo"],
            "preocupado": ["preocupado", "ansioso", "inquieto", "angustiado"],
            "confundido": ["confundido", "perdido", "duda", "incertidumbre"],
            "enojado": ["enojado", "molesto", "frustrado", "irritado"],
            "esperanzado": ["esperanza", "fe", "confianza", "creer"]
        }

        text_lower = text.lower()
        for state, indicators in emotional_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return state
        return "neutral"

    def _generate_empathetic_error_response(self, lang: str = 'es') -> str:
        """Genera una respuesta de error empática."""
        responses = {
            'es': ("Disculpa, en este momento no puedo procesar completamente tu pregunta. "
                  "¿Podrías reformularla de otra manera? Estoy aquí para ayudarte."),
            'tzo': "Mi jcholbun ava`i. ¿Mi xu` xachaꞌcholbun yan vuelta?"
        }
        return responses.get(lang, responses['es'])

    def _generate_personal_insight(self, interpretation: Dict[str, Any]) -> str:
        """Genera una perspectiva personal basada en la interpretación."""
        insights = interpretation.get("insights", [])
        if insights:
            return f"Me gustaría compartir contigo esta perspectiva: {insights[0]}"
        return "Permíteme compartir contigo algunas reflexiones importantes."

    def _generate_meditation_points(self, interpretation: Dict[str, Any]) -> List[str]:
        """Genera puntos de meditación personalizada."""
        base_points = interpretation.get("steps", [])[:2]
        if not base_points:
            base_points = ["Reflexiona sobre el significado personal de este pasaje",
                         "Considera cómo aplicar estas verdades en tu vida diaria"]
        return base_points

    def _generate_explanation(self, interpretation: Dict[str, Any]) -> str:
        """Genera una explicación teológica estructurada."""
        steps = interpretation.get("steps", [])
        errors = interpretation.get("errores_comunes", [])

        explanation = []
        if steps:
            explanation.append("Pasos para entender este texto:")
            explanation.extend([f"{idx + 1}. {step}" for idx, step in enumerate(steps)])

        if errors:
            explanation.append("\nErrores comunes a evitar:")
            explanation.extend([f"- {error}" for error in errors])

        return "\n".join(explanation)

    def _generate_practical_application(self, interpretation: Dict[str, Any]) -> str:
        """Genera una aplicación práctica personalizada."""
        return (
            "Medita en este pasaje y pide a Dios sabiduría para aplicarlo en tu vida diaria. "
            "¿Cómo podrías poner en práctica esta verdad hoy mismo?"
        )