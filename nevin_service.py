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
            Cuando el usuario tiene un nombre, debes referirte a él usando su nombre de forma natural y amigable.

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

    def _generate_fallback_response(self, question: str) -> Dict[str, Any]:
        """Genera una respuesta usando solo GPT-4 cuando FAISS/DB no están disponibles."""
        try:
            fallback_prompt = """Como asistente bíblico experto, proporciona una respuesta basada en tu conocimiento de la Biblia y los escritos de Elena G. White. 
            Incluye referencias bíblicas específicas y citas textuales de Elena G. White con sus referencias de libros.
            
            FORMATO DE RESPUESTA:
            1. Explicación bíblica con versículos específicos
            2. Citas relevantes de Elena G. White con referencias exactas de libros
            3. Aplicación práctica
            
            Pregunta: {question}"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_context},
                    {"role": "user", "content": fallback_prompt.format(question=question)}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                'response': response.choices[0].message.content,
                'success': True,
                'source': 'fallback'
            }
        except Exception as e:
            logger.error(f"Error en fallback: {str(e)}")
            return {
                'response': "Lo siento, no puedo generar una respuesta en este momento.",
                'success': False,
                'source': 'error'
            }

    def process_query(self, question: str, conversation_history: List[Dict[str, str]] = None, user_id: str = None) -> Dict[str, Any]:
        """Procesa consultas del usuario manteniendo el contexto conversacional."""
        try:
            if conversation_history is None:
                conversation_history = []
            
            # Obtener historial completo del usuario
            if user_id:
                from models import Conversation, User
                from database import db
                
                # Obtener información del usuario
                user = User.query.get(user_id)
                user_context = {
                    "username": user.username if user else None,
                    "preferences": user.preferences if hasattr(user, 'preferences') else {},
                    "last_active": user.last_seen if hasattr(user, 'last_seen') else None
                }
                
                # Obtener últimas 20 conversaciones para contexto más amplio
                past_conversations = Conversation.query.filter_by(user_id=user_id)\
                    .order_by(Conversation.timestamp.desc())\
                    .limit(20)\
                    .all()
                
                # Analizar patrones de interés
                conversation_themes = {}
                for conv in past_conversations:
                    for theme in self._extract_themes(conv.question):
                        conversation_themes[theme] = conversation_themes.get(theme, 0) + 1
                
                context = {
                    "user_info": user_context,
                    "conversation_patterns": conversation_themes,
                    "recent_interactions": [
                        {"question": c.question, "response": c.response, 
                         "timestamp": c.timestamp.isoformat(),
                         "emotion": c.emotion if hasattr(c, 'emotion') else None}
                        for c in past_conversations[:5]
                    ]
                }
                
                conversation_history = self._enrich_context(conversation_history, context)
                

            # Inicializar KnowledgeBaseManager
            kb_manager = KnowledgeBaseManager()
            
            # Añadir contexto de la conversación
            context = "\n\nContexto de la conversación:\n"
            if conversation_history:
                for msg in conversation_history[-3:]:  # Últimos 3 mensajes
                    context += f"{'Usuario' if msg['role'] == 'user' else 'Nevin'}: {msg['content']}\n"
                    
            # Intentar obtener resultados de FAISS/DB
            try:
                if not kb_manager.initialize():
                    logger.warning("FAISS no disponible, usando fallback")
                    return self._generate_fallback_response(question)
                    
                results = kb_manager.search_knowledge_base(question, top_k=5)
                if not results:
                    logger.warning("No se encontraron resultados en FAISS, usando fallback")
                    return self._generate_fallback_response(question)
            except Exception as e:
                logger.warning(f"Error al buscar en FAISS: {e}, usando fallback")
                return self._generate_fallback_response(question)

            # Inicializar y buscar contenido una sola vez
            if not kb_manager.initialize():
                logger.error("Error inicializando KnowledgeBaseManager")
                return self._generate_error_response("Error de inicialización del sistema")

            # Buscar contenido relevante con parámetros optimizados
            try:
                results = kb_manager.search_knowledge_base(question, top_k=5)
                if not results:
                    logger.warning("No se encontraron resultados relevantes")
                    return self._generate_fallback_response(question)
            except Exception as e:
                logger.error(f"Error en búsqueda de conocimiento: {str(e)}")
                return self._generate_fallback_response(question)

            # Preparar contexto con citas de EGW
            egw_context = self._prepare_egw_context(results)

            # Generar respuesta enriquecida
            chat_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_context + self.principles_context + context
                    },
                    {
                        "role": "user",
                        "content": f"""Analiza profundamente esta consulta y proporciona una respuesta detallada:

Pregunta: {question}

Contexto EGW disponible:
{egw_context}

Estructura tu respuesta con:
1. Análisis bíblico profundo con múltiples referencias
2. Conexiones con los escritos de Elena G. White
3. Aplicaciones prácticas específicas
4. Ilustraciones o analogías relevantes
5. Conclusión que inspire a la acción"""
                    }
                ],
                temperature=0.7,  # Reducido para mayor precisión
                max_tokens=2500,  # Aumentado para respuestas más detalladas
                presence_penalty=0.3,  # Ajustado para mejor coherencia
                frequency_penalty=0.5,  # Balanceado para variedad natural
                top_p=0.95  # Ajustado para mayor precisión
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

    def _enrich_context(self, conversation_history: List[Dict[str, str]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enriches the conversation history with user context."""
        enriched_history = conversation_history.copy()
        enriched_history.insert(0, {"role": "context", "content": context})
        return enriched_history

    def _extract_themes(self, text: str) -> List[str]:
        """Extracts themes from text (needs implementation based on your theme extraction logic)."""
        # Placeholder - Replace with actual theme extraction logic.
        # This example simply splits the text into words as themes
        return text.lower().split()