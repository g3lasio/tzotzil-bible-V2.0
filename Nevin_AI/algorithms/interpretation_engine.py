import json
from typing import Dict, Any


class InterpretationEngine:
    """Motor para interpretar textos bíblicos basado en principios hermenéuticos."""

    def __init__(self, principles_file: str):
        """Inicializa el motor con un archivo de principios."""
        self.principles = self._load_principles(principles_file)

    def _load_principles(self, file_path: str) -> Dict[str, Any]:
        """Carga principios desde un archivo JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def interpret(self, text: str, text_type: str) -> Dict[str, Any]:
        """Interpreta un texto bíblico basado en su tipo."""
        for principle in self.principles["interpretation_principles"]:
            if principle["type"] == text_type:
                return {
                    "message_central":
                    principle["principles"],
                    "steps": [
                        ex["steps"] for ex in principle.get("examples", [])
                        if ex["text"] == text
                    ],
                    "errors":
                    principle["common_errors"]
                }
        return {
            "error": "No se encontraron principios para este tipo de texto."
        }


def classify_question(question: str) -> str:
    """Clasifica la pregunta en categorías conocidas."""
    categories = [
        "pregunta doctrinal", "pregunta emocional", "consulta general",
        "pregunta avanzada", "pregunta bíblica específica"
    ]
    # GPT-4 clasifica la intención
    response = prompt_manager.generate_structured_response(
        f"Clasifica la siguiente pregunta en una de las categorías: {categories}. "
        f"Pregunta: {question}")
    return response
