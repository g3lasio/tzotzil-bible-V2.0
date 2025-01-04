"""
Sistema de autenticación simplificado usando JWT
"""
from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
import logging
from validation import DataValidator

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
    if not token:
        logger.warning("Intento de validación con token vacío")
        return None
    logger.info("Iniciando validación de token")

    try:
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token inválido")
        return None
    except Exception as e:
        logger.error(f"Error validando token: {str(e)}")
        return None

def get_token_from_request():
    """Extrae el token JWT de la solicitud"""
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            return auth_header.split(" ")[1]
        except IndexError:
            return None
    return request.cookies.get('token')

def token_required(f):
    """Decorador para proteger rutas"""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            if request.endpoint not in ['auth.login', 'auth.register', 'auth.forgot_password', 'static']:
                flash('Por favor inicia sesión para acceder', 'warning')
                return redirect(url_for('auth.login'))

        payload = validate_token(token)
        if not payload:
            return redirect(url_for('auth.login'))

        try:
            current_user = User.query.get(payload['sub'])
            if not current_user or not current_user.is_active:
                return redirect(url_for('auth.login'))

            # Verificar acceso a Nevin
            if request.endpoint and 'nevin' in request.endpoint:
                if not current_user.has_nevin_access():
                    flash('Necesitas una suscripción premium o estar en período de prueba para acceder a Nevin', 'warning')
                    return redirect(url_for('routes.index'))
                    
            return f(current_user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            return redirect(url_for('auth.login'))
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401
            if not current_user.is_active:
                return jsonify({'message': 'Usuario inactivo'}), 401

            return f(current_user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            return jsonify({'message': 'Error de autenticación'}), 500

    return decorated

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el login de usuarios"""
    logger.info(f"Método de solicitud: {request.method}")
    
    if request.method == 'GET':
        return render_template('auth/login.html')

    try:
        data = request.form
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        logger.info(f"Intento de login para usuario: {email}")
        logger.info(f"Remember me activado: {data.get('remember_me', False)}")

        # Validar campos
        if not email or not password:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter(User.email == email).first()

        if user and user.check_password(password):
            logger.info(f"Generando token para usuario ID: {user.id}")
            token = generate_token(user.id)
            if not token:
                logger.error("Fallo en generación de token")
                flash('Error generando token de sesión', 'error')
                return redirect(url_for('auth.login'))
            logger.info("Token generado exitosamente")

            # Actualizar última conexión antes de generar respuesta
            user.last_login = datetime.utcnow()
            db.session.commit()

            response = redirect(url_for('routes.index'))
            response.set_cookie(
                'token', 
                token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=86400 * JWT_EXPIRATION_DAYS,
                domain=None  # Permitir cualquier dominio
            )
            
            # Actualizar última conexión
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Inicio de sesión exitoso', 'success')
            return response

        flash('Credenciales inválidas', 'error')
        return redirect(url_for('auth.login'))

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        flash('Error en el servidor', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevo usuario"""
    if request.method == 'GET':
        return render_template('auth/signup.html')

    try:
        data = request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()

        # Validar datos del usuario
        validator = DataValidator()
        errors = validator.validate_user_data(email=email, username=username, password=password)

        if password != confirm_password:
            errors.append("Las contraseñas no coinciden")

        if not data.get('terms'):
            errors.append("Debes aceptar los términos y condiciones")

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está registrado', 'error')
            return redirect(url_for('auth.register'))

        # Crear nuevo usuario con período de prueba
        user = User(
            username=username,
            lastname=data.get('lastname', ''),
            phone=data.get('phone', ''),
            email=email,
            is_active=True,
            plan_type='Free',
            trial_started_at=datetime.utcnow(),
            trial_ends_at=datetime.utcnow() + timedelta(days=21),
            nevin_access=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.id)
        if not token:
            flash('Error generando token de sesión', 'error')
            return redirect(url_for('auth.login'))

        response = redirect(url_for('routes.index'))
        response.set_cookie(
            'token',
            token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=86400 * JWT_EXPIRATION_DAYS
        )

        flash('¡Bienvenido! Tu cuenta ha sido creada exitosamente. Disfruta de tu período de prueba de 21 días con acceso completo a todas las funcionalidades.', 'success')
        return render_template('auth/email/welcome.html', username=username)

    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        db.session.rollback()
        flash('Error en el servidor', 'error')
        return redirect(url_for('auth.register'))

@auth.route('/me')
@token_required
def get_user(current_user):
    """Obtiene información del usuario actual"""
    try:
        return jsonify(current_user.to_dict()), 200
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Maneja la recuperación de contraseña"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generar código de recuperación
            reset_code = ''.join(random.choices('0123456789', k=6))
            user.reset_code = reset_code
            user.reset_code_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            flash('Se ha enviado un código de recuperación a tu email', 'success')
            return redirect(url_for('auth.reset_password'))
            
        flash('Email no encontrado', 'error')
    return render_template('auth/forgot_password.html')

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    """Cierra la sesión del usuario actual"""
    try:
        response = redirect(url_for('auth.login'))
        response.delete_cookie('token')
        flash('Sesión cerrada exitosamente', 'success')
        return response
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        flash('Error al cerrar sesión', 'error')
        return redirect(url_for('auth.login'))

def init_login_manager(app):
    """Initialize the login manager for backward compatibility"""
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

import random