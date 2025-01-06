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
import random

logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)

# Centralizar configuración de JWT
JWT_ALGORITHM = 'HS256'

def generate_token(user_id, is_refresh_token=False):
    """Genera un token JWT para el usuario"""
    try:
        expiration = current_app.config['JWT_REFRESH_TOKEN_EXPIRES'] if is_refresh_token else current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        payload = {
            'exp': datetime.utcnow() + expiration,
            'iat': datetime.utcnow(),
            'sub': str(user_id),
            'type': 'refresh' if is_refresh_token else 'access'
        }
        logger.debug(f"Generando token con payload: {payload}")
        secret_key = current_app.config.get('SECRET_KEY')
        logger.debug(f"Usando SECRET_KEY: {secret_key[:4]}...")
        
        token = jwt.encode(
            payload,
            secret_key,
            algorithm=JWT_ALGORITHM
        )
        logger.info(f"Token generado exitosamente para usuario {user_id}")
        return token
    except Exception as e:
        logger.error(f"Error generando token: {str(e)}")
        return None

def validate_token(token):
    """Valida y decodifica un token JWT con verificaciones mejoradas"""
    if not token:
        logger.warning("Intento de validación con token vacío")
        return None

    try:
        # Verificar formato del token
        if not isinstance(token, str) or not token.count('.') == 2:
            logger.warning("Formato de token inválido")
            return None

        # Obtener configuración
        secret_key = current_app.config.get('JWT_SECRET_KEY', current_app.config.get('SECRET_KEY'))
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        leeway = current_app.config.get('JWT_LEEWAY', 10)  # 10 segundos de margen

        # Decodificar y validar token
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            options={
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "leeway": leeway
            }
        )

        # Validaciones adicionales
        if 'type' not in payload or payload['type'] not in ['access', 'refresh']:
            logger.warning("Token sin tipo válido")
            return None

        if 'sub' not in payload:
            logger.warning("Token sin subject")
            return None

        logger.info(f"Token validado exitosamente para usuario {payload.get('sub')}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error validando token: {str(e)}")
        return None
    
    try:
        logger.debug(f"Validando token: {token[:10]}...")
        secret_key = current_app.config.get('JWT_SECRET_KEY', current_app.config.get('SECRET_KEY'))
        logger.debug(f"Usando JWT_SECRET_KEY para validación")
        
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": True}
        )
        logger.info(f"Token validado exitosamente. User ID: {payload.get('sub')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error validando token: {str(e)}")
        return None

def get_token_from_request():
    """Extrae el token JWT de la solicitud"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(" ")[1]
    token = request.cookies.get('token')
    if token:
        return token
    return None

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
            current_user = User.query.filter_by(id=payload['sub']).first()
            if not current_user or not current_user.is_active:
                flash('Usuario inactivo o no encontrado', 'error')
                return redirect(url_for('auth.login'))

            if request.endpoint and 'nevin' in request.endpoint:
                if not current_user.has_nevin_access():
                    flash('Necesitas una suscripción premium o estar en período de prueba para acceder a Nevin', 'warning')
                    return redirect(url_for('routes.index'))

            return f(current_user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            flash('Error de autenticación', 'error')
            return redirect(url_for('auth.login'))

    return decorated

# Authentication API Documentation
"""
Base URL: /api/auth
Available endpoints:
- POST /api/auth/login: User login
- POST /api/auth/register: New user registration 
- GET /api/auth/me: Get current user info
- POST /api/auth/logout: User logout
- POST /api/auth/forgot-password: Password recovery
"""

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    User authentication endpoint
    
    Methods:
        GET: Returns login page
        POST: Authenticates user
        
    POST body:
    {
        "email": string,
        "password": string,
        "remember_me": boolean
    }
    
    Returns:
        200: Login successful + JWT token
        401: Invalid credentials
        400: Missing/invalid fields
    """
    logger.info(f"Método de solicitud: {request.method}")
    
    if request.method == 'GET':
        return render_template('auth/login.html')

    try:
        data = request.form
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        remember_me = data.get('remember_me', False)
        
        logger.info(f"Intento de login para usuario: {email}")
        logger.info(f"Remember me activado: {remember_me}")

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

            user.last_login = datetime.utcnow()
            db.session.commit()

            response = redirect(url_for('routes.index'))
            max_age = 86400 * 30 if remember_me else 86400  # 30 días o 1 día
            response.set_cookie(
                'token', 
                token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=max_age,
                path='/'
            )
            
            # Agregar header para el frontend
            response.headers['X-Auth-Token'] = token
            
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

        user = User(
            username=username,
            lastname=data.get('lastname', '').strip(),
            phone=data.get('phone', '').strip(),
            email=email,
            is_active=True,
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
            secure=False,
            samesite='Lax',
            max_age=86400 * JWT_EXPIRATION_DAYS,
            path='/'
        )

        flash('¡Bienvenido! Tu cuenta ha sido creada exitosamente. Disfruta de tu período de prueba de 21 días.', 'success')
        return response

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

@auth.route('/logout')
def logout():
    """Cierra la sesión del usuario actual"""
    try:
        response = redirect(url_for('auth.login'))
        response.delete_cookie('token', path='/')
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


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Maneja el proceso de recuperación de contraseña"""
    if request.method == 'GET':
        return render_template('auth/forgot_password.html')
        
    try:
        email = request.form.get('email')
        if not email:
            flash('Por favor ingresa tu correo electrónico', 'error')
            return redirect(url_for('auth.forgot_password'))
            
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No existe una cuenta con ese correo electrónico', 'error')
            return redirect(url_for('auth.forgot_password'))

        # Generar código de recuperación
        reset_code = ''.join(random.choices('0123456789', k=6))
        user.reset_code = reset_code
        user.reset_code_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # Aquí se enviaría el email con el código
        flash('Se ha enviado un código de recuperación a tu correo electrónico', 'success')
        return redirect(url_for('auth.reset_password'))
        
    except Exception as e:
        logger.error(f"Error en recuperación de contraseña: {str(e)}")
        flash('Error en el servidor', 'error')
        return redirect(url_for('auth.forgot_password'))


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """Maneja el reseteo de contraseña con código de verificación"""
    if request.method == 'GET':
        return render_template('auth/reset_password.html')
        
    try:
        code = request.form.get('code')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not code or not password or not confirm_password:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('auth.reset_password'))
            
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('auth.reset_password'))
            
        user = User.query.filter_by(reset_code=code).first()
        if not user or not user.reset_code_expires or user.reset_code_expires < datetime.utcnow():
            flash('Código inválido o expirado', 'error')
            return redirect(url_for('auth.reset_password'))
            
        user.set_password(password)
        user.reset_code = None
        user.reset_code_expires = None
        db.session.commit()
        
        flash('Tu contraseña ha sido actualizada exitosamente', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        logger.error(f"Error en reseteo de contraseña: {str(e)}")
        flash('Error en el servidor', 'error')
        return redirect(url_for('auth.reset_password'))