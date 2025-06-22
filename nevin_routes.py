import logging
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from attached_assets.chat_request import get_ai_response

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

nevin_bp = Blueprint('nevin', __name__, url_prefix='/nevin')
api_nevin_bp = Blueprint('api_nevin', __name__, url_prefix='/api/nevin')

def init_nevin_routes(app):
    """Inicializa las rutas de Nevin"""
    try:
        if not app:
            logger.error("Se recibió una instancia de app nula")
            return False

        app.register_blueprint(nevin_bp)
        app.register_blueprint(api_nevin_bp)
        logger.info("Nevin blueprints registrados correctamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando rutas Nevin: {str(e)}")
        return False

@nevin_bp.route('/')
def nevin_page():
    """Renderiza la página principal de Nevin."""
    try:
        return render_template('nevin.html')
    except Exception as e:
        logger.error(f"Error en nevin_page: {str(e)}")
        return render_template('error.html', error="Hubo un problema al cargar la página."), 500

@nevin_bp.route('/query', methods=['POST'])
def nevin_query():
    """Procesa las consultas a la API de Nevin"""
    try:
        data = request.get_json()
        if not data:
            logger.error("No se recibieron datos en la consulta")
            return jsonify({
                'response': "No se recibieron datos en la consulta.",
                'success': False,
                'error': 'missing_data'
            }), 400

        question = data.get('question', '').strip()
        if not question:
            logger.warning("Se recibió una pregunta vacía")
            return jsonify({
                'response': "Por favor, escribe tu pregunta.",
                'success': False,
                'error': 'empty_question'
            }), 400

        context = data.get('context', '')
        language = data.get('language', 'Spanish')
        user_preferences = data.get('preferences', {})

        logger.info(f"Procesando consulta: {question[:50]}...")
        response = get_ai_response(
            question=question,
            context=context,
            language=language,
            user_preferences=user_preferences
        )

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error procesando consulta: {str(e)}")
        return jsonify({
            'response': "Hubo un error procesando tu pregunta. Por favor, inténtalo de nuevo.",
            'success': False,
            'error': str(e)
        }), 500

@api_nevin_bp.route('/chat', methods=['POST'])
def api_nevin_chat():
    """API endpoint for Nevin chat - same as nevin_query but under /api/nevin/chat"""
    try:
        data = request.get_json()
        if not data:
            logger.error("No se recibieron datos en la consulta")
            return jsonify({
                'response': "No se recibieron datos en la consulta.",
                'success': False,
                'error': 'missing_data'
            }), 400

        question = data.get('question', '').strip()
        if not question:
            logger.warning("Se recibió una pregunta vacía")
            return jsonify({
                'response': "Por favor, escribe tu pregunta.",
                'success': False,
                'error': 'empty_question'
            }), 400

        context = data.get('context', '')
        language = data.get('language', 'Spanish')
        user_preferences = data.get('preferences', {})

        logger.info(f"Procesando consulta API: {question[:50]}...")
        response = get_ai_response(
            question=question,
            context=context,
            language=language,
            user_preferences=user_preferences
        )

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error procesando consulta API: {str(e)}")
        return jsonify({
            'response': "Hubo un error procesando tu pregunta. Por favor, inténtalo de nuevo.",
            'success': False,
            'error': str(e)
        }), 500