"""
Sistema de autenticación simplificado usando JWT
"""
from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
import logging

logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)

def generate_token(user_id):
    """Genera un token JWT para el usuario"""
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        logger.error(f"Error generando token: {str(e)}")
        return None

def token_required(f):
    """Decorador para proteger rutas"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token mal formado'}), 401

        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401

        try:
            data = jwt.decode(
                token, 
                current_app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            current_user = User.query.get(data['sub'])
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        except Exception as e:
            logger.error(f"Error validando token: {str(e)}")
            return jsonify({'message': 'Error al procesar token'}), 500

    return decorated

@auth.route('/auth/login', methods=['POST'])
def login():
    """Inicio de sesión de usuario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Faltan credenciales'}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Credenciales inválidas'}), 401

        token = generate_token(user.id)
        if not token:
            return jsonify({'message': 'Error generando token'}), 500

        return jsonify({
            'token': token,
            'user_id': user.id,
            'email': user.email
        }), 200

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500

@auth.route('/auth/register', methods=['POST'])
def register():
    """Registro de nuevo usuario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400

        email = data.get('email')
        password = data.get('password')
        username = data.get('username', email.split('@')[0])

        if not email or not password:
            return jsonify({'message': 'Faltan datos requeridos'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'El email ya está registrado'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'El nombre de usuario ya está registrado'}), 400

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.id)
        if not token:
            return jsonify({'message': 'Error generando token'}), 500

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'token': token,
            'user_id': user.id
        }), 201

    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Error en el servidor'}), 500

@auth.route('/auth/me', methods=['GET'])
@token_required
def get_user(current_user):
    """Obtiene información del usuario actual"""
    try:
        return jsonify({
            'id': current_user.id,
            'email': current_user.email,
            'username': current_user.username
        }), 200
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500

def init_login_manager(app):
    """Initialize the login manager"""
    from flask_login import LoginManager
    try:
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except Exception as e:
                logger.error(f"Error cargando usuario: {str(e)}")
                return None

        return login_manager
    except Exception as e:
        logger.error(f"Error inicializando login manager: {str(e)}")
        raise