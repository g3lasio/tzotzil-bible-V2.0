from typing import Dict, Any


class EnhancedResponseManager:
    """Clase para enriquecer las respuestas generadas por Nevin."""

    def __init__(self, interpretation_engine):
        """
        Inicializa el gestor de respuestas con un motor de interpretación.
        :param interpretation_engine: Instancia de InterpretationEngine.
        """
        self.interpretation_engine = interpretation_engine

    def generate_response(self, query: str, text_type: str) -> Dict[str, Any]:
        """
        Genera una respuesta enriquecida y formateada.
        :param query: Consulta del usuario.
        :param text_type: Tipo de texto bíblico identificado.
        :return: Respuesta enriquecida con formato estructurado.
        """
        interpretation = self.interpretation_engine.interpret(query, text_type)
        if "error" not in interpretation:
            response = (
                f"🌟 **Introducción:**\n"
                f"Gracias por tu pregunta. Es un tema relevante y muy valioso para explorar.\n\n"
                f"📖 **Base Bíblica:**\n{interpretation.get('principios', 'Sin principios disponibles')}\n\n"
                f"📚 **Explicación Teológica:**\n{self._generate_explanation(interpretation)}\n\n"
                f"💡 **Aplicación Práctica:**\nMedita en este pasaje y pide a Dios sabiduría para aplicarlo en tu vida diaria."
            )
            return {"response": response, "success": True}
        else:
            return {
                "response":
                "No pude interpretar este texto. Por favor, intenta reformular tu pregunta.",
                "success": False
            }

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

    def _format_interpretation(self, interpretation: Dict[str, Any]) -> str:
        """
        Formatea la interpretación en un mensaje estructurado.
        :param interpretation: Resultado de la interpretación.
        :return: Texto formateado para el usuario.
        """
        steps = "\n".join([
            f"{idx + 1}. {step}"
            for idx, step in enumerate(interpretation.get("steps", []))
        ])
        return (
            f"**Mensaje Central:**\n{interpretation.get('message_central', '')}\n\n"
            f"**Pasos de Interpretación:**\n{steps}\n\n"
            f"**Errores a Evitar:**\n- " +
            "\n- ".join(interpretation.get("errors", [])))
