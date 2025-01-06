import logging
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required, current_user
from auth import token_required
from attached_assets.chat_request import get_ai_response

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

nevin_bp = Blueprint('nevin', __name__, url_prefix='/nevin')

def init_nevin_routes(app):
    """Inicializa las rutas de Nevin"""
    try:
        if not app:
            logger.error("Se recibió una instancia de app nula")
            return False

        app.register_blueprint(nevin_bp)
        logger.info("Nevin blueprint registrado correctamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando rutas Nevin: {str(e)}")
        return False

@nevin_bp.route('/')
@token_required
def nevin_page(current_user):
    """Renderiza la página principal de Nevin."""
    try:
        if not current_user.has_nevin_access():
            flash('Tu período de prueba ha terminado. Actualiza a Premium para continuar usando Nevin.', 'warning')
            return redirect(url_for('routes.index'))

        user_name = current_user.username.split('@')[0] if '@' in current_user.username else current_user.username
        welcome_message = f"¡Hola {user_name}! Soy Nevin, tu asistente bíblico. ¿En qué puedo ayudarte?"

        return render_template('nevin.html', 
                           welcome_message=welcome_message,
                           user_name=user_name)
    except Exception as e:
        logger.error(f"Error en nevin_page: {str(e)}")
        return render_template('error.html', error="Hubo un problema al cargar la página."), 500

@nevin_bp.route('/query', methods=['POST'])
@token_required
def nevin_query(current_user):
    """Procesa las consultas a la API de Nevin"""
    try:
        if not current_user.has_nevin_access():
            return jsonify({
                'response': "Necesitas una suscripción premium para usar Nevin.",
                'success': False,
                'error': 'no_access'
            }), 403

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