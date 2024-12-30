
import json
from typing import Dict, List, Optional

class InterpretationHandler:
    def __init__(self):
        self.principles = self._load_interpretation_principles()

    def _load_interpretation_principles(self) -> Dict:
        with open('Nevin_AI/data/principios_de_interpretacion.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_interpretation_context(self, text_type: str) -> Dict:
        """Obtiene el contexto de interpretación basado en el tipo de texto."""
        for principle in self.principles['interpretation_principles']:
            if principle['type'].lower() == text_type.lower():
                return {
                    'principles': principle['principles'],
                    'examples': principle['examples'],
                    'common_errors': principle['common_errors']
                }
        return {}

    def enhance_response(self, text_type: str, response: str) -> str:
        """Enriquece la respuesta con principios de interpretación relevantes."""
        context = self.get_interpretation_context(text_type)
        if not context:
            return response

        enhanced_response = response + "\n\n<div class='interpretation-box'>\n"
        enhanced_response += "<h4>Principios de Interpretación Aplicables:</h4>\n<ul>"
        
        for principle in context['principles'][:2]:  # Limitamos a 2 principios más relevantes
            enhanced_response += f"\n<li>{principle['name']}: {principle['description']}</li>"
        
        enhanced_response += "</ul>\n</div>"
        return enhanced_response
