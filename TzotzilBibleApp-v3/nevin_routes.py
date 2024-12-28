from datetime import datetime
import asyncio
from functools import wraps
import logging
from typing import Dict, Any, Optional, Tuple

from flask import (Blueprint, render_template, request, jsonify, flash,
                   redirect, url_for, current_app)
from flask_login import login_required, current_user
from extensions import db
from models import User
from database import db_manager
from Nevin_AI.prompt_manager import PromptManager

# Configurar logger
logger = logging.getLogger(__name__)

try:
    prompt_manager = PromptManager()
except Exception as e:
    logger.error(f"Error inicializando PromptManager: {e}")
    prompt_manager = None

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Crear blueprint
nevin_bp = Blueprint('nevin_bp', __name__)

# Inicializar prompt_manager global
prompt_manager = None


class NevinServiceManager:
    """Manager simplificado de servicio Nevin."""
    _instance = None

    def __init__(self):
        self.service = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = NevinServiceManager()
        return cls._instance

    def get_service(self):
        return self.service

    def init_service(self, app):
        """Inicializa el servicio Nevin con manejo de errores mejorado."""
        try:
            from .nevin_service import NevinService
            from .Nevin_AI.algorithms.indexer import Indexer
            
            if not hasattr(db_manager, "check_health"):
                logger.error(
                    "El método check_health no está definido en DatabaseManager."
                )
                return None

            with app.app_context():
                health_status = db_manager.check_health()
                if not health_status.get('is_healthy', False):
                    logger.error(
                        f"Database health check failed: {health_status.get('error', 'Unknown error')}"
                    )
                    return None

                logger.info("Iniciando servicio Nevin...")
                self.service = NevinService(app)

                if not hasattr(self.service, 'check_user_access'):
                    logger.error(
                        "Servicio Nevin no tiene los métodos requeridos")
                    return None

                logger.info("Servicio Nevin inicializado correctamente")
                return self.service

        except ImportError as e:
            logger.error(f"Error importando módulos necesarios: {str(e)}")
            return None
        except Exception as e:
            logger.error(
                f"Error crítico inicializando servicio Nevin: {str(e)}",
                exc_info=True)
            return None


nevin_service_manager = NevinServiceManager.get_instance()


@nevin_bp.record_once
def on_register(state):
    """Se ejecuta una vez cuando el blueprint se registra en la aplicación."""
    app = state.app
    logger.info("Registrando blueprint Nevin...")
    try:
        with app.app_context():
            try:
                service = nevin_service_manager.init_service(app)
                if not service:
                    logger.error(
                        "No se pudo inicializar el servicio Nevin durante el registro del blueprint"
                    )
                    raise RuntimeError(
                        "Fallo en la inicialización del servicio Nevin")
            except ImportError as e:
                logger.error(f"Error importando módulos necesarios: {str(e)}")
                raise
            except Exception as e:
                logger.error(
                    f"Error inesperado inicializando servicio: {str(e)}")
                raise
            else:
                logger.info("Blueprint Nevin registrado exitosamente")
    except Exception as e:
        logger.error(f"Error inicializando servicio Nevin: {str(e)}")


def handle_nevin_errors(f):
    """Decorador para manejar errores de manera consistente."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {f.__name__}: {str(e)}")
            return jsonify({
                "error": "Error interno",
                "details": "Hubo un problema al procesar tu solicitud.",
                "debug_info": str(e) if current_app.debug else None
            }), 500

    return decorated_function


@nevin_bp.route('/', methods=['GET'])
@login_required
def nevin_page():
    """Renderiza la página principal de Nevin."""
    try:
        access_details = None
        nevin_service = nevin_service_manager.get_service()
        if nevin_service:
            try:
                access_details = nevin_service.get_access_details(
                    current_user.id)
            except Exception as service_error:
                logger.warning(
                    f"Error obteniendo detalles de acceso: {service_error}")
                access_details = None

        username = current_user.username if current_user else 'Amigo'
        user_id = current_user.id if current_user else None

        logger.info(
            f"Renderizando Nevin para usuario: {username} (ID: {user_id})")

        return render_template('nevin.html',
                               welcome_message=f"¡Hola, {username}!",
                               access_details=access_details,
                               user_id=user_id)
    except Exception as e:
        logger.error(f"Error en nevin_page: {str(e)}", exc_info=True)
        return render_template(
            'error.html',
            error="Hubo un problema al procesar tu solicitud."), 500


@nevin_bp.before_request
def setup_service():
    """Asegura que PromptManager y otros servicios estén disponibles antes de manejar la solicitud."""
    global prompt_manager
    if not prompt_manager:
        try:
            prompt_manager = PromptManager()
        except Exception as e:
            logger.error(f"No se pudo inicializar PromptManager: {str(e)}",
                         exc_info=True)
            raise RuntimeError("Error crítico al inicializar PromptManager.")


@nevin_bp.before_request
def validate_session():
    """Validar la sesión del usuario antes de manejar cualquier solicitud."""
    if not current_user.is_authenticated:
        logger.warning("Sesión no válida. Usuario no autenticado.")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "error": "Sesión no válida",
                "details": "Por favor, inicia sesión nuevamente.",
                "redirect": url_for('auth.login')
            }), 401
        else:
            return redirect(url_for('auth.login'))
    else:
        logger.info(f"Usuario autenticado: {current_user.username}")


@nevin_bp.route('/query', methods=['POST'])
@login_required
async def nevin_query():
    """Procesa consultas enviadas a Nevin verificando caché, acceso y utilizando la jerarquía de respuestas."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        user_id = data.get('user_id')

        if not question or not user_id:
            logger.error(
                "La consulta no contiene todos los parámetros necesarios.")
            return jsonify({
                'response':
                "Faltan datos en la solicitud. Por favor, incluye tu pregunta y tu ID de usuario.",
                'success': False
            }), 400

        logger.info(f"Procesando consulta para usuario {user_id}: {question}")
        nevin_service = nevin_service_manager.get_service()

        if not nevin_service:
            logger.error(
                "Servicio Nevin no disponible - Intentando reinicializar...")
            nevin_service = nevin_service_manager.init_service(current_app)

        if not nevin_service:
            logger.error("Fallo en la reinicialización del servicio")
            return jsonify({
                'response':
                "El servicio Nevin no está disponible en este momento. Por favor, inténtalo más tarde.",
                'success': False,
                'error_details': "Service initialization failed"
            }), 503

        if not hasattr(nevin_service,
                       'prompt_manager') or not nevin_service.prompt_manager:
            logger.error("Componentes críticos no disponibles")
            return jsonify({
                'response':
                "El servicio está en mantenimiento. Por favor, inténtalo más tarde.",
                'success': False,
                'error_details': "Critical components unavailable"
            }), 503

        response_data = await nevin_service.process_query(question, user_id)

        if response_data.get('success'):
            return jsonify(response_data), 200
        else:
            return jsonify(response_data), 500

    except Exception as e:
        logger.error(f"Error interno procesando la consulta: {str(e)}",
                     exc_info=True)
        return jsonify({
            'response':
            "Ocurrió un error interno al procesar tu solicitud. Por favor, intenta de nuevo más tarde.",
            'success': False
        }), 500
