"""
Sistema de autenticación simplificado usando JWT
"""
from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
import logging

logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)

# Centralizar configuración de JWT
JWT_EXPIRATION_DAYS = 1
JWT_ALGORITHM = 'HS256'

def generate_token(user_id):
    """Genera un token JWT para el usuario"""
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm=JWT_ALGORITHM
        )
    except Exception as e:
        logger.error(f"Error generando token: {str(e)}")
        return None

def validate_token(token):
    """Valida y decodifica un token JWT"""
    try:
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorador para proteger rutas"""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'No se proporcionó token de autorización'}), 401

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'message': 'Token mal formado'}), 401

        payload = validate_token(token)
        if not payload:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        try:
            current_user = User.query.get(payload['sub'])
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401
            if not current_user.is_active:
                return jsonify({'message': 'Usuario inactivo'}), 401

            return f(current_user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            return jsonify({'message': 'Error de autenticación'}), 500

    return decorated

def validate_credentials(data):
    """Valida las credenciales proporcionadas"""
    errors = []
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email:
        errors.append('El email es requerido')
    if not password:
        errors.append('La contraseña es requerida')

    return errors, email, password

@auth.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    """Inicio de sesión de usuario"""
    try:
        data = request.get_json() if request.is_json else request.form
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400

        errors, email, password = validate_credentials(data)
        if errors:
            return jsonify({'message': 'Error de validación', 'errors': errors}), 400

        user = User.query.filter(
            db.or_(User.email == email, User.username == email)
        ).first()

        if not user or not user.check_password(password):
            logger.warning(f"Intento de login fallido para: {email}")
            return jsonify({'message': 'Credenciales inválidas'}), 401

        if not user.is_active:
            logger.warning(f"Intento de login con cuenta inactiva: {email}")
            return jsonify({'message': 'Usuario inactivo'}), 401

        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user)
        token = generate_token(user.id)

        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Error en el servidor'}), 500

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

        errors, email, password = validate_credentials(data)
        if errors:
            return jsonify({'message': 'Error de validación', 'errors': errors}), 400

        username = data.get('username', email.split('@')[0])

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'El email ya está registrado'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'El nombre de usuario ya está registrado'}), 400

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.id)
        if not token:
            return jsonify({'message': 'Error generando token'}), 500

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
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

@auth.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Cierra la sesión del usuario actual"""
    try:
        # Aquí podríamos implementar una lista negra de tokens si fuera necesario
        return jsonify({
            'message': 'Sesión cerrada exitosamente'
        }), 200
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        return jsonify({'message': 'Error al cerrar sesión'}), 500

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