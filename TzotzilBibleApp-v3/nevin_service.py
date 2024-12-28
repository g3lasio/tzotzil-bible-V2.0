import os
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from enum import Enum
from dataclasses import dataclass
from cachetools import TTLCache
import re
from spellchecker import SpellChecker
from models import User, NevinAccess, db
from azure_openai_config import openai_config
from .nevin_utils import NevinUtils
from .Nevin_AI.algorithms.indexer import Indexer
from .Nevin_AI.algorithms.interpretation_engine import InterpretationEngine
from .Nevin_AI.algorithms.enhanced_response_manager import EnhancedResponseManager
from .Nevin_AI.bible_data import BibleData
from .Nevin_AI.knowledge_base_manager import KnowledgeBaseManager
from .Nevin_AI.prompts import PromptManager
from .Nevin_AI.algorithms.text_type_identifier import TextTypeIdentifier

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccessType(Enum):
    NONE = "none"
    TRIAL = "trial"
    PREMIUM = "premium"
    ERROR = "error"


@dataclass
class AccessDetails:
    access_type: AccessType
    message: str
    features: List[str]
    time_remaining: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class NevinService:
    """Servicio principal para la funcionalidad de Nevin con caché y procesamiento asíncrono."""

    def __init__(self, app=None, cache_ttl: int = 3600):
        """Inicializa el servicio de Nevin con sistema de caché."""
        self.app = app
        self.nevin_utils = NevinUtils(app)
        self.client = None

        # Sistema de caché
        self.response_cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        self.user_context_cache = TTLCache(maxsize=500, ttl=cache_ttl)

        # Cola de procesamiento asíncrono
        self.processing_queue = asyncio.Queue()
        self.background_tasks = set()

        self._initialize_components()

    def preprocess_question(question: str) -> str:
        """Limpia y normaliza la pregunta del usuario."""
        # Corregir ortografía
        spell = SpellChecker(language='es')
        words = question.split()
        corrected_words = [spell.correction(word) for word in words]
        corrected_question = " ".join(corrected_words)

        # Quitar caracteres especiales y normalizar
        cleaned_question = re.sub(r'[^a-zA-ZáéíóúñÑ0-9\s]', '',
                                  corrected_question).strip()
        return cleaned_question

    def enrich_question(question: str) -> str:
        """Añade contexto y estructura a preguntas simples."""
        keywords = ["gracia", "fe", "salvación",
                    "pecado"]  # Palabras clave comunes
        for keyword in keywords:
            if keyword in question:
                return f"Explícame {keyword} en un contexto bíblico teológico."
        return question

    def _initialize_components(self):
        """Inicializa todos los componentes necesarios."""
        required_components = {
            'text_type_identifier': False,
            'bible_data': False,
            'interpretation_engine': False,
            'response_manager': False,
            'knowledge_base': False,
            'prompt_manager': False
        }

        try:
            self.text_type_identifier = TextTypeIdentifier()
            required_components['text_type_identifier'] = True
            logger.info("TextTypeIdentifier inicializado correctamente")

            self.bible_data = BibleData()
            required_components['bible_data'] = True
            logger.info("BibleData inicializado correctamente")

            self.interpretation_engine = InterpretationEngine(
                "Nevin_AI/data/principios_de_interpretacion.json")
            required_components['interpretation_engine'] = True
            logger.info("Motor de interpretación inicializado correctamente")

            self.response_manager = EnhancedResponseManager(
                self.interpretation_engine)
            required_components['response_manager'] = True
            logger.info("Gestor de respuestas enriquecidas inicializado correctamente")

            # Importar el módulo indexer desde la ubicación correcta
            from .Nevin_AI.algorithms.indexer import Indexer
            self.indexer = Indexer("Nevin_AI/nevin_knowledge")
            self.knowledge_base_manager = KnowledgeBaseManager(db)
            required_components['knowledge_base'] = True
            logger.info("KnowledgeBaseManager inicializado correctamente")

            self.prompt_manager = PromptManager()
            required_components['prompt_manager'] = True
            logger.info("PromptManager inicializado correctamente")

            # Verificar inicialización completa
            failed_components = [k for k, v in required_components.items() if not v]
            if failed_components:
                raise RuntimeError(f"Componentes no inicializados: {', '.join(failed_components)}")

            logger.info("Todos los componentes inicializados correctamente")
            return True

        except Exception as e:
            logger.error(f"Error crítico inicializando componentes: {str(e)}")
            logger.error(f"Componentes fallidos: {[k for k, v in required_components.items() if not v]}")
            raise RuntimeError(f"Error de inicialización: {str(e)}")

    def _personalize_response(self, response: str, username: str) -> str:
        """Personaliza la respuesta con el nombre del usuario y un tono amigable."""
        greetings = [
            f"¡Hola {username}! 😊",
            f"¡Qué bueno verte de nuevo, {username}! 🌟",
            f"¡{username}, me alegra que preguntes eso! 💡",
            f"¡Excelente pregunta, {username}! 🎯",
        ]

        transitions = [
            "¡Déjame bucear en mi base de datos celestial! ✨",
            "¡Permíteme consultar mi biblioteca divina! 📚",
            "¡Vamos a explorar juntos esta interesante pregunta! 🔍",
            "¡Ah, uno de mis temas favoritos! 🌟"
        ]

        from random import choice
        greeting = choice(greetings)
        transition = choice(transitions)

        return f"{greeting}\n\n{transition}\n\n{response}"

    async def _get_cached_response(self,
                                   cache_key: str) -> Optional[Dict[str, Any]]:
        """Obtiene una respuesta cacheada."""
        return self.response_cache.get(cache_key)

    async def _verify_access_async(self, user_id: int) -> Tuple[bool, str]:
        """Verifica el acceso de forma asíncrona."""
        try:
            cache_key = f"access_{user_id}"
            cached_access = self.user_context_cache.get(cache_key)
            if cached_access:
                return cached_access

            has_access, message = self._verify_access(user_id)
            self.user_context_cache[cache_key] = (has_access, message)
            return has_access, message

        except Exception as e:
            logger.error(f"Error en verificación asíncrona: {str(e)}")
            return False, f"Error de verificación: {str(e)}"

    def _verify_access(self, user_id: int) -> Tuple[bool, str]:
        """Verifica si un usuario tiene acceso a Nevin."""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Usuario no encontrado"

            logger.info(f"Verificando acceso para usuario {user_id}")
            return True, "Acceso de desarrollo activo"

        except Exception as e:
            logger.error(f"Error verificando acceso: {str(e)}")
            return False, f"Error de verificación: {str(e)}"

    def _get_latest_access(self, user_id: int) -> Optional[NevinAccess]:
        """Obtiene el último acceso registrado para un usuario."""
        try:
            return NevinAccess.query.filter_by(user_id=user_id)\
                .order_by(NevinAccess.created_at.desc())\
                .first()
        except Exception as e:
            logger.error(f"Error obteniendo último acceso: {str(e)}")
            return None

    def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Obtiene el contexto del usuario para personalizar respuestas."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {}

            return {
                'user_type': 'premium' if user.is_premium else 'regular',
                'spiritual_level':
                'advanced' if user.is_premium else 'beginner'
            }
        except Exception as e:
            logger.error(f"Error obteniendo contexto de usuario: {str(e)}")
            return {}

    async def process_query(self, question: str,
                            user_id: int) -> Dict[str, Any]:
        """Procesa una consulta de usuario usando una jerarquía simplificada."""
        try:
            if not hasattr(self, 'prompt_manager') or not self.prompt_manager:
                logger.error("PromptManager no está inicializado.")
                return {
                    "response": "Error interno. PromptManager no está disponible.",
                    "success": False,
                    "source_type": "error",
                    "details": "Prompt manager initialization error"
                }

            user = User.query.get(user_id)
            username = user.username if user else "amigo"

            cache_key = f"{user_id}_{question}"
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                logger.info(
                    f"Respuesta encontrada en caché para usuario {username}")
                cached_response['response'] = self._personalize_response(
                    cached_response['response'], username)
                return cached_response

            has_access, message = await self._verify_access_async(user_id)
            if not has_access:
                return {
                    'response': f"No tienes acceso activo a Nevin: {message}",
                    'success': False,
                    'source_type': 'access_denied',
                    'details': None
                }

            return await self._process_query_layers(question, username,
                                                    cache_key)

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            return {
                'response':
                "Lo siento, hubo un error al procesar tu consulta. Por favor, intenta de nuevo.",
                'success': False,
                'source_type': 'error',
                'details': str(e)
            }

    async def _process_query_layers(self, question: str, username: str,
                                    cache_key: str) -> Dict[str, Any]:
        """Procesa la consulta a través de las diferentes capas de búsqueda."""
        # Primera Capa: SQLite + FAISS
        bible_results = await self.bible_data.search_verses(question)
        theological_results, _ = await self.knowledge_base_manager.search_related_content(
            question)

        if bible_results or theological_results:
            combined_response = await self.prompt_manager.generate_structured_response(
                f"Basado en los resultados:\n\nVersículos:\n{bible_results}\n\nComentarios:\n{theological_results}"
            )
            response_data = {
                'response': combined_response,
                'success': True,
                'source_type': 'combined',
                'details': {
                    'bible_verses': len(bible_results),
                    'theological_refs': len(theological_results)
                }
            }
            self.response_cache[cache_key] = response_data
            return response_data

        # Segunda Capa: Interpretación Bíblica
        logger.info("Activando motor de interpretación bíblica.")
        text_type = self.text_type_identifier.identify(question)
        if text_type == "desconocido":
            logger.warning("Tipo de texto no identificado, usando 'narrativa'")
            text_type = "narrativa"

        enriched_response = await self.response_manager.generate_response(
            question, text_type)
        if enriched_response.get("success"):
            response_data = {
                'response': enriched_response["response"],
                'success': True,
                'source_type': 'interpretation',
                'details': enriched_response.get("interpretation_details", {})
            }
            self.response_cache[cache_key] = response_data
            return response_data

        # Tercera Capa: Respuesta Predeterminada
        logger.info("Activando respuesta predeterminada con GPT-4")
        fallback_response = await self.prompt_manager.generate_structured_response(
            "Por favor, responde a esta pregunta con una reflexión bíblica, cita relevante de EGW y una invitación espiritual:"
        )
        return {
            'response': fallback_response,
            'success': True,
            'source_type': 'fallback',
            'details': None
        }

    def check_user_access(self,
                          user_id: Optional[int] = None) -> Tuple[bool, str]:
        """Verifica el acceso de un usuario."""
        if not user_id:
            return False, "Usuario no identificado"
        return self._verify_access(user_id)

    def get_access_details(self,
                           user_id: Optional[int] = None) -> AccessDetails:
        """Obtiene los detalles de acceso para un usuario."""
        try:
            if not user_id:
                return AccessDetails(
                    access_type=AccessType.NONE,
                    message="Por favor inicia sesión para acceder a Nevin",
                    features=["chat_básico"],
                    error=None)

            has_access, access_message = self._verify_access(user_id)
            if not has_access:
                return AccessDetails(access_type=AccessType.NONE,
                                     message="Sin acceso activo a Nevin",
                                     features=["vista_previa"],
                                     error=None)

            user = User.query.get(user_id)
            if user and user.is_premium:
                return AccessDetails(access_type=AccessType.PREMIUM,
                                     message="Acceso premium activo",
                                     features=[
                                         "chat_avanzado", "búsqueda_teológica",
                                         "recursos_premium"
                                     ],
                                     time_remaining=None)

            access = self._get_latest_access(user_id)
            if access:
                time_remaining = access.access_until - datetime.utcnow()
                return AccessDetails(
                    access_type=AccessType.TRIAL,
                    message="Acceso temporal activo",
                    features=["chat_básico", "búsqueda_básica"],
                    time_remaining={
                        "days": time_remaining.days,
                        "hours": time_remaining.seconds // 3600
                    })

            return AccessDetails(access_type=AccessType.NONE,
                                 message="Sin acceso activo a Nevin",
                                 features=["vista_previa"],
                                 error=None)

        except Exception as e:
            logger.error(f"Error obteniendo detalles de acceso: {str(e)}")
            return AccessDetails(access_type=AccessType.ERROR,
                                 message="Error al verificar acceso",
                                 features=[],
                                 error=str(e))

    def upgrade_to_premium(self, user_id: int) -> Tuple[bool, str]:
        """Actualiza un usuario a premium."""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Usuario no encontrado"

            user.is_premium = True
            user.save()

            return True, "Usuario actualizado a premium exitosamente"
        except Exception as e:
            logger.error(f"Error actualizando a premium: {str(e)}")
            return False, f"Error en actualización: {str(e)}"

    async def generate_response(self, query: str, context: Dict[str,
                                                                Any]) -> str:
        """Genera una respuesta estructurada usando GPT-4."""
        try:
            prompt = self._build_prompt(query, context)

            if not self.client:
                raise ValueError("Cliente OpenAI no inicializado")

            response = await asyncio.to_thread(
                lambda: self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{
                        "role":
                        "system",
                        "content":
                        """Eres Nevin, un asistente teológico experto que proporciona respuestas 
                            profundas y elegantes, equilibrando claridad para principiantes con profundidad para expertos.
                            Usa las referencias proporcionadas para dar respuestas precisas y bien fundamentadas."""
                    }, {
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.7,
                    max_tokens=1000))

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return "Lo siento, hubo un error al generar la respuesta. Por favor, intenta de nuevo."

    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Construye el prompt para GPT-4."""
        return f"Responde a la siguiente consulta:\n\n{query}\n\nContexto:\n{context}"