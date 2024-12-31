import logging
from flask import Blueprint, render_template, request, jsonify, session
from attached_assets.chat_request import get_ai_response

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
nevin_bp = Blueprint('nevin_bp', __name__)

def init_nevin_service(app):
    """Inicializa el servicio de Nevin"""
    try:
        from nevin_service import NevinService
        app.nevin_service = NevinService(app)
        logger.info("Servicio Nevin inicializado correctamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando servicio Nevin: {str(e)}")
        return False

@nevin_bp.route('/')
def nevin_page():
    """Renderiza la página principal de Nevin."""
    try:
        return render_template('nevin.html', 
                           welcome_message="¡Hola! Soy Nevin, tu asistente bíblico. ¿En qué puedo ayudarte?")
    except Exception as e:
        logger.error(f"Error en nevin_page: {str(e)}")
        return render_template('error.html', 
                           error="Hubo un problema al cargar la página."), 500

@nevin_bp.route('/download_seminar/<filename>')
def download_seminar(filename):
    """Sirve el archivo PDF del seminario."""
    try:
        seminars_dir = os.path.join('static', 'seminars')
        return send_from_directory(seminars_dir, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error sirviendo PDF: {str(e)}")
        return jsonify({'error': str(e)}), 404

@nevin_bp.route('/query', methods=['POST'])
def nevin_query():
    """Procesa consultas enviadas a Nevin."""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        if not data:
            return jsonify({
                'response': "No se recibieron datos en la consulta.",
                'success': False
            }), 400

        question = data.get('question', '').strip()
        if not question:
            return jsonify({
                'response': "Por favor, escribe tu pregunta.",
                'success': False
            }), 400

        # Obtener el contexto de la conversación si existe
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