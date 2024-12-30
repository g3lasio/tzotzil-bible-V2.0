import logging
from flask import render_template, request, jsonify, session
from app import app
from models import BibleVerse, EGWWriting, Conversation, User
from chat_request import get_ai_response
from db import db
import uuid
import random

# Configure logging
logger = logging.getLogger(__name__)

# Pool of suggested questions
SUGGESTED_QUESTIONS_POOL = [
    "¿Qué enseña la Biblia sobre la oración?",
    "¿Cómo puedo fortalecer mi fe?",
    "¿Qué dice la Biblia sobre el amor al prójimo?",
    "¿Cuál es la importancia del sábado?",
    "¿Qué nos enseña la Biblia sobre la salvación?",
    "¿Cómo puedo estudiar mejor la Biblia?",
    "¿Qué dice la Biblia sobre el Espíritu Santo?",
    "¿Cómo puedo tener una mejor vida devocional?",
    "¿Qué enseña la Biblia sobre el perdón?",
    "¿Cómo puedo compartir mi fe con otros?",
    "¿Qué dice la Biblia sobre la segunda venida?",
    "¿Cómo puedo resistir las tentaciones?",
    "¿Qué enseña la Biblia sobre el bautismo?",
    "¿Cómo puedo encontrar paz en momentos difíciles?",
    "¿Qué dice la Biblia sobre la familia?"
]

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {str(error)}")
    return jsonify({
        "success": False,
        "error": "Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta nuevamente."
    }), 500

@app.before_request
def before_request():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    if 'language' not in session:
        session['language'] = 'Spanish'
        
    # Get or create user based on session_id
    try:
        user = User.query.filter_by(session_id=session['session_id']).first()
        if not user:
            user = User(
                session_id=session['session_id'],
                preferences={'language': session['language']}
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user with session_id: {session['session_id']}")
    except Exception as e:
        logger.error(f"Error in user management: {str(e)}")

@app.route('/egw-stats')
def egw_stats():
    stats = {}
    stats['total_writings'] = EGWWriting.query.count()
    stats['books'] = db.session.query(EGWWriting.book).distinct().count()
    stats['languages'] = db.session.query(EGWWriting.language).distinct().all()
    
    # Obtener lista de libros y cantidad de citas por libro
    book_stats = db.session.query(
        EGWWriting.book, 
        db.func.count(EGWWriting.id)
    ).group_by(EGWWriting.book).all()
    
    stats['books_detail'] = [
        {'book': book, 'count': count} 
        for book, count in book_stats
    ]
    
    return jsonify(stats)

@app.route('/')
def index():
    user = User.query.filter_by(session_id=session['session_id']).first()
    has_previous_conversations = Conversation.query.filter_by(user_id=user.id).first() is not None
    
    # Get user's name from preferences or use default
    user_name = user.preferences.get('name', '') if user.preferences else ''
    
    welcome_message = {
        "content": (
            f"¡Hola {user_name}! Qué gusto verte de nuevo. ¿En qué puedo ayudarte hoy?"
            if has_previous_conversations and user_name else
            "¡Hola! Soy Nevin, tu amigo y asistente virtual. Para hacer esto más personal, ¿podrías decirme tu nombre?"
            if not user_name else
            f"¡Hola {user_name}! Soy Nevin, tu amigo y asistente virtual. Me encanta conversar y ayudarte a encontrar respuestas a tus preguntas. ¿En qué puedo ayudarte hoy?"
        ),
        "type": "assistant"
    }
    
    # Randomly select 3 questions from the pool
    suggested_questions = random.sample(SUGGESTED_QUESTIONS_POOL, 3)
    
    return render_template('index.html', 
                         welcome_message=welcome_message,
                         suggested_questions=suggested_questions)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        question = data.get('question')
        language = session.get('language', 'Spanish')
        
        if not question:
            return jsonify({
                "success": False,
                "error": "Question is required"
            }), 400
        
        # Get user and their preferences
        user = User.query.filter_by(session_id=session['session_id']).first()
        if not user:
            return jsonify({
                "success": False,
                "error": "User session not found"
            }), 400
        
        # Get recent conversation context
        recent_conversations = Conversation.query.filter(
            (Conversation.user_id == user.id) | 
            (Conversation.session_id == session['session_id'])
        ).order_by(Conversation.timestamp.desc()).limit(5).all()
        
        # Format context to include both questions and responses
        context = "\n".join([
            f"Usuario: {c.question}\nNevin: {c.response}"
            for c in reversed(recent_conversations)
        ])
        
        # Get AI response with user preferences
        response_data = get_ai_response(
            question=question,
            context=context,
            language=language,
            user_preferences={
                'user_id': user.id,
                'session_id': session['session_id']
            }
        )
        
        # Check if the response was successful
        if not response_data.get('success', False):
            return jsonify(response_data), 500

        # Save conversation if there's a valid response
        if 'response' in response_data:
            conversation = Conversation(
                user_id=user.id,
                session_id=session['session_id'],
                question=question,
                response=response_data['response'],
                language=language
            )
            db.session.add(conversation)
            db.session.commit()
            logger.info(f"Saved conversation for user {user.id}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta nuevamente."
        }), 500

@app.route('/api/update-name', methods=['POST'])
def update_user_name():
    try:
        data = request.json
        name = data.get('name')
        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
            
        user = User.query.filter_by(session_id=session['session_id']).first()
        if user:
            user.preferences = user.preferences or {}
            user.preferences['name'] = name
            db.session.commit()
            return jsonify({'success': True})
            
    except Exception as e:
        logger.error(f"Error updating user name: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error updating user name'
        }), 500

@app.route('/api/conversation-history', methods=['GET'])
def get_conversation_history():
    try:
        user = User.query.filter_by(session_id=session['session_id']).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User session not found'
            }), 400
            
        conversations = Conversation.query.filter(
            (Conversation.user_id == user.id) | 
            (Conversation.session_id == session['session_id'])
        ).order_by(Conversation.timestamp.desc()).all()
        
        history = [{
            'question': conv.question,
            'response': conv.response,
            'timestamp': conv.timestamp.isoformat()
        } for conv in conversations]
        
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error retrieving conversation history'
        }), 500

@app.route('/api/switch-language', methods=['POST'])
def switch_language():
    try:
        data = request.json
        language = data.get('language')
        if language in ['Spanish', 'Tzotzil']:
            session['language'] = language
            
            # Update user preferences
            user = User.query.filter_by(session_id=session['session_id']).first()
            if user:
                user.preferences = user.preferences or {}
                user.preferences['language'] = language
                db.session.commit()
                
            logger.info(f"Switched language to {language}")
            return jsonify({'success': True})
        return jsonify({
            'success': False,
            'error': 'Invalid language'
        })
    except Exception as e:
        logger.error(f"Error switching language: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })
