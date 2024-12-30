import logging
import os
import asyncio
from typing import Dict, Any, List
from openai import OpenAI
from Nevin_AI.knowledge_base_manager import KnowledgeBaseManager
from Nevin_AI.algorithms.enhanced_response_manager import EnhancedResponseManager
from Nevin_AI.algorithms.interpretation_engine import InterpretationEngine
import json

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NevinService:
    """Servicio Nevin enfocado en respuestas bíblicas y pastorales."""

    def __init__(self, app=None):
        """Inicializa el servicio Nevin."""
        self.app = app
        self.client = None
        self.principles_path = "Nevin_AI/data/principios_de_interpretacion.json"

        try:
            # Verificar y obtener API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY no está configurada")
                raise ValueError("OPENAI_API_KEY no está configurada")

            # Inicializar cliente OpenAI
            self.client = OpenAI(api_key=api_key)

            # Inicializar componentes de procesamiento
            self.interpretation_engine = InterpretationEngine(self.principles_path)
            self.response_manager = EnhancedResponseManager(self.interpretation_engine)

            # Cargar principios
            with open(self.principles_path, 'r', encoding='utf-8') as f:
                self.principles = json.load(f)
                self.principles_context = "\n\nPrincipios de Interpretación:\n" + "\n".join([f"- {p}" for p in self.principles])

            self.system_context = """Eres Nevin, un asistente pastoral y bíblico cálido y sabio que valora la concisión. 
            Tu propósito es ayudar a las personas a comprender mejor la Biblia y conectar emocionalmente con ellas.

            PERSONALIDAD:
            - Muestra empatía genuina y comprensión
            - Usa un tono conversacional y amigable
            - Incluye toques de humor apropiado cuando sea oportuno
            - Mantén un balance entre profundidad espiritual y accesibilidad

            ESTRUCTURA DE RESPUESTAS:
            1. Conexión emocional inicial
            2. Respuesta basada en sabiduría bíblica
            3. Referencias relevantes (bíblicas y de Elena G. White)
            4. Aplicación práctica y personal
            5. Invitación al diálogo continuo

            IMPORTANTE:
            - Adapta tu tono según el estado emocional detectado
            - Usa analogías cotidianas para explicar conceptos profundos
            - Mantén un balance entre guía espiritual y conversación natural
            - Sé genuino y auténtico en tus respuestas"""

            logger.info("Servicio Nevin inicializado correctamente")

        except Exception as e:
            logger.error(f"Error en la inicialización de NevinService: {str(e)}")
            raise

    async def search_egw_content(self, query: str) -> List[Dict[str, Any]]:
        """Busca contenido relevante en los escritos de EGW."""
        try:
            kb_manager = KnowledgeBaseManager()
            results = await kb_manager.search_related_content(query, threshold=0.7)
            return results[0] if results and len(results) > 0 else []
        except Exception as e:
            logger.error(f"Error buscando contenido de EGW: {e}")
            return []

    def process_query(self, question: str) -> Dict[str, Any]:
        """Procesa consultas del usuario con un enfoque pastoral y bíblico."""
        try:
            # Inicializar KnowledgeBaseManager
            kb_manager = KnowledgeBaseManager()
            if not kb_manager.initialize():
                logger.error("Error inicializando KnowledgeBaseManager")
                return self._generate_error_response("Error de inicialización del sistema")

            # Buscar contenido relevante con parámetros ajustados
            results = kb_manager.search_knowledge_base(question, top_k=5)

            # Preparar contexto con citas de EGW
            egw_context = self._prepare_egw_context(results)

            # Generar respuesta enriquecida
            chat_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_context + self.principles_context
                    },
                    {
                        "role": "user",
                        "content": f"Pregunta: {question}\n\nContexto disponible de EGW:{egw_context}"
                    }
                ],
                temperature=0.9,
                max_tokens=1500,
                presence_penalty=0.8,
                frequency_penalty=0.7,
                top_p=0.98
            )

            # Procesar y enriquecer la respuesta
            base_response = chat_response.choices[0].message.content
            enhanced_response = self.response_manager.generate_response(
                query=question,
                text_type="conversation"
            )

            if enhanced_response["success"]:
                final_response = self._combine_responses(base_response, enhanced_response["response"])
            else:
                final_response = base_response

            logger.info(f"Respuesta generada exitosamente para: {question[:50]}...")

            return {
                'response': final_response,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return self._generate_error_response("Error procesando la consulta")

    def _prepare_egw_context(self, results: List[Dict[str, Any]]) -> str:
        """Prepara el contexto con citas de EGW."""
        if not results:
            return " No se encontraron citas específicas, pero responderé basándome en principios bíblicos y el espíritu de los escritos de Elena G. White."

        egw_context = "\n\nReferencias de Elena G. White relevantes:\n"
        for result in results[:3]:
            if isinstance(result['content'], str) and len(result['content'].strip()) > 0:
                source_info = result.get('source', 'Desconocido')
                egw_context += f"- {result['content']} ({source_info})\n"
        return egw_context

    def _combine_responses(self, base_response: str, enhanced_response: str) -> str:
        """Combina la respuesta base con la respuesta enriquecida."""
        # Mantener la estructura mejorada pero incorporar contenido relevante de la respuesta base
        return enhanced_response

    def _generate_error_response(self, message: str) -> Dict[str, Any]:
        """Genera una respuesta de error amigable."""
        return {
            'response': f"Lo siento, tuve un problema procesando tu pregunta. {message} Por favor, inténtalo de nuevo en unos momentos.",
            'success': False
        }