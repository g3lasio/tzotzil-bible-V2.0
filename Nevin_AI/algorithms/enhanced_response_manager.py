from typing import Dict, Any


class EnhancedResponseManager:
    """Clase para enriquecer las respuestas generadas por Nevin."""

    def __init__(self, interpretation_engine):
        """
        Inicializa el gestor de respuestas con un motor de interpretación.
        :param interpretation_engine: Instancia de InterpretationEngine.
        """
        self.interpretation_engine = interpretation_engine
        self.conversation_context = {"emotional_state": "neutral", "conversation_depth": 0}

    def generate_response(self, query: str, text_type: str) -> Dict[str, Any]:
        """
        Genera una respuesta enriquecida y formateada.
        :param query: Consulta del usuario.
        :param text_type: Tipo de texto identificado.
        :return: Respuesta enriquecida con formato estructurado.
        """
        # Analizar estado emocional y contexto
        emotional_state = self._analyze_emotional_state(query)
        self.conversation_context["emotional_state"] = emotional_state
        self.conversation_context["conversation_depth"] += 1

        # Generar interpretación base
        interpretation = self.interpretation_engine.interpret(query, text_type)

        if "error" not in interpretation:
            # Adaptar el formato según el contexto emocional
            response = self._format_response_by_context(interpretation, emotional_state)
            return {"response": response, "success": True}
        else:
            return {
                "response": self._generate_empathetic_error_response(),
                "success": False
            }

    def _analyze_emotional_state(self, text: str) -> str:
        """
        Analiza el estado emocional del texto.
        :param text: Texto a analizar.
        :return: Estado emocional identificado.
        """
        # Palabras clave para diferentes estados emocionales
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

    def _format_response_by_context(self, interpretation: Dict[str, Any], emotional_state: str) -> str:
        """
        Formatea la respuesta según el contexto emocional.
        :param interpretation: Interpretación base.
        :param emotional_state: Estado emocional detectado.
        :return: Respuesta formateada.
        """
        # Personalizar introducción según estado emocional
        intro_phrases = {
            "alegre": "¡Qué hermoso es compartir tu alegría! ",
            "triste": "Comprendo tu dolor y estoy aquí para acompañarte. ",
            "preocupado": "Entiendo tu preocupación. Permíteme compartir algo que puede ayudarte. ",
            "confundido": "Es normal sentirse así. Vamos a explorar esto juntos. ",
            "enojado": "Veo que esta situación te afecta profundamente. ",
            "esperanzado": "Tu fe es inspiradora. ",
            "neutral": "Gracias por compartir conmigo. "
        }

        intro = intro_phrases.get(emotional_state, intro_phrases["neutral"])

        # Construir respuesta estructurada
        if self.conversation_context["conversation_depth"] > 1:
            # Para conversaciones más profundas, usar un formato más personal
            response = (
                f"{intro}"
                f"{self._generate_personal_insight(interpretation)}\n\n"
                f"💭 **Reflexión:**\n{interpretation.get('principios', 'Sin principios disponibles')}\n\n"
                f"💡 **Para meditar:**\n{self._generate_meditation_points(interpretation)}"
            )
        else:
            # Para primeras interacciones, mantener un formato más estructurado
            response = (
                f"{intro}\n\n"
                f"📖 **Base Bíblica:**\n{interpretation.get('principios', 'Sin principios disponibles')}\n\n"
                f"📚 **Explicación:**\n{self._generate_explanation(interpretation)}\n\n"
                f"💡 **Aplicación Práctica:**\n{self._generate_practical_application(interpretation)}"
            )

        return response

    def _generate_personal_insight(self, interpretation: Dict[str, Any]) -> str:
        """
        Genera una perspectiva personal basada en la interpretación.
        """
        insights = interpretation.get("insights", [])
        if insights:
            return f"Me gustaría compartir contigo esta perspectiva: {insights[0]}"
        return "Permíteme compartir contigo algunas reflexiones importantes."

    def _generate_meditation_points(self, interpretation: Dict[str, Any]) -> str:
        """
        Genera puntos de meditación personalizada.
        """
        steps = interpretation.get("steps", [])
        if steps:
            points = "\n".join([f"• {step}" for step in steps[:2]])
            return f"Te invito a reflexionar sobre estos puntos:\n{points}"
        return "Toma un momento para meditar en estas verdades y su significado para tu vida."

    def _generate_practical_application(self, interpretation: Dict[str, Any]) -> str:
        """
        Genera una aplicación práctica personalizada.
        """
        return ("Medita en este pasaje y pide a Dios sabiduría para aplicarlo en tu vida diaria. "
                "¿Cómo podrías poner en práctica esta verdad hoy mismo?")

    def _generate_empathetic_error_response(self) -> str:
        """
        Genera una respuesta de error empática.
        """
        return ("Disculpa, en este momento no puedo procesar completamente tu pregunta. "
                "¿Podrías reformularla de otra manera? Estoy aquí para ayudarte.")

    def _generate_explanation(self, interpretation: Dict[str, Any]) -> str:
        """
        Genera una explicación teológica basada en los principios de interpretación.
        :param interpretation: Resultado de la interpretación.
        :return: Explicación estructurada.
        """
        pasos = "\n".join([
            f"{idx + 1}. {step}"
            for idx, step in enumerate(interpretation.get("steps", []))
        ])
        errores = "\n".join([
            f"- {error}"
            for error in interpretation.get("errores_comunes", [])
        ])
        return (f"Pasos para entender este texto:\n{pasos}\n\n"
                f"Errores comunes a evitar:\n{errores}")