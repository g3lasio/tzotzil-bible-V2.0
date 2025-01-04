import logging
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from attached_assets.chat_request import get_ai_response
from auth import token_required # Added import statement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nevin_bp = Blueprint('nevin_bp', __name__)

def init_nevin_routes(app):
    """Inicializa las rutas de Nevin"""
    try:
        app.register_blueprint(nevin_bp, url_prefix='/nevin')
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
            
        return render_template('nevin.html', 
                           welcome_message="¡Hola! Soy Nevin, tu asistente bíblico. ¿En qué puedo ayudarte?")
    except Exception as e:
        logger.error(f"Error en nevin_page: {str(e)}")
        return render_template('error.html', error="Hubo un problema al cargar la página."), 500

@nevin_bp.route('/query', methods=['POST'])
def nevin_query():
    """Procesa consultas enviadas a Nevin."""
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
        user_id = session.get('user_id')
        
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
            'success': False
        }), 500