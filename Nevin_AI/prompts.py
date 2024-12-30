"""
Sistema de gestión de prompts mejorado para Nevin
"""
class PromptManager:
    def __init__(self):
        self.system_prompt = """Soy un asistente bíblico y teológico entrenado para proporcionar respuestas precisas y fundamentadas, 
        integrando referencias bíblicas y escritos de Elena G. White. Mi objetivo es ayudar en el estudio y comprensión de las 
        verdades bíblicas, manteniendo un enfoque pastoral y empático."""

        self.context_memory = []
        self.max_context_length = 5

    def get_chat_prompt(self, query, emotional_state="neutral", conversation_depth=0):
        """
        Genera un prompt enriquecido basado en el contexto y estado emocional

        Args:
            query: Consulta del usuario
            emotional_state: Estado emocional detectado
            conversation_depth: Profundidad de la conversación

        Returns:
            Dict con el prompt formateado
        """
        # Construir contexto basado en interacciones previas
        context = "\n".join(self.context_memory[-self.max_context_length:])

        # Ajustar el tono según el estado emocional
        emotional_guidance = {
            "triste": "con empatía y consuelo",
            "preocupado": "con seguridad y esperanza",
            "confundido": "con claridad y paciencia",
            "alegre": "con entusiasmo y afirmación",
            "enojado": "con calma y comprensión",
            "neutral": "con objetividad y precisión"
        }

        tone = emotional_guidance.get(emotional_state, "con objetividad y precisión")

        return {
            "role": "system",
            "content": f"{self.system_prompt}\n\nContexto previo:\n{context}\n\nResponde {tone}, "
                      f"usando referencias bíblicas relevantes y citas de Elena G. White cuando sea apropiado. "
                      f"Profundidad de respuesta: {'detallada' if conversation_depth > 1 else 'básica'}"
        }

    def update_context(self, interaction):
        """
        Actualiza el contexto de la conversación

        Args:
            interaction: Nueva interacción para agregar al contexto
        """
        self.context_memory.append(interaction)
        if len(self.context_memory) > self.max_context_length:
            self.context_memory.pop(0)

    def format_response(self, response, include_references=True):
        """
        Formatea la respuesta para mantener consistencia en la presentación

        Args:
            response: Respuesta a formatear
            include_references: Si se deben incluir referencias

        Returns:
            Respuesta formateada
        """
        if not include_references:
            return response

        # Formatear referencias bíblicas
        formatted_response = response.replace(
            '[BIBLE]', '<div class="bible-reference">'
        ).replace('[/BIBLE]', '</div>')

        # Formatear citas de EGW
        formatted_response = formatted_response.replace(
            '[EGW]', '<div class="egw-quote">'
        ).replace('[/EGW]', '</div>')

        return formatted_response