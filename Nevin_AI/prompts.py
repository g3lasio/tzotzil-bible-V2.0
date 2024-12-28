
class PromptManager:
    def __init__(self):
        self.system_prompt = """Soy un asistente bíblico y teológico entrenado para proporcionar respuestas precisas y fundamentadas."""
        
    def get_chat_prompt(self, query):
        return {
            "role": "system",
            "content": self.system_prompt
        }

    def format_response(self, response):
        return response
