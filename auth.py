"""
Sistema de autenticación mejorado con login social y recuperación por código
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, LoginManager
from models import User, db
from flask_mail import Message
from extensions import mail
import random
from datetime import datetime, timedelta
from flask_dance.contrib.google import make_google_blueprint, google
import jwt
import logging

logger = logging.getLogger(__name__)
login_manager = LoginManager()

def init_login_manager(app):
    """Initialize the login manager"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
    login_manager.login_message_category = 'info'

    # Registrar el loader aquí para asegurar que esté disponible
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user: {str(e)}")
            return None

    return login_manager

auth = Blueprint('auth', __name__)

def send_reset_code(email, code):
    """Envía el código de recuperación por email"""
    try:
        msg = Message('Código de Recuperación - Nevin',
                     sender='gelasio@chyrris.com',
                     recipients=[email])
        msg.html = render_template('auth/email/reset_code.html',
                               code=code)
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending reset code: {str(e)}")
        return False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        try:
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()

            if user and user.check_password(password):
                login_user(user, remember=bool(remember))
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash('¡Inicio de sesión exitoso!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('routes.index'))

            flash('Usuario o contraseña inválidos', 'error')
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            flash('Error al intentar iniciar sesión', 'error')

    return render_template('auth/login.html')

@auth.route('/request-reset', methods=['POST'])
def request_reset():
    """Solicitar código de recuperación"""
    email = request.form.get('email')
    if not email:
        return {'error': 'Email requerido'}, 400

    user = User.query.filter_by(email=email).first()
    if user:
        code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        user.reset_code = code
        user.reset_code_expires = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

        if send_reset_code(email, code):
            return {'message': 'Código enviado'}, 200

    return {'message': 'Si el email existe, recibirás un código'}, 200

@auth.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """Verificar código de recuperación"""
    email = request.form.get('email')
    code = request.form.get('code')

    user = User.query.filter_by(email=email).first()
    if user and user.reset_code == code and \
       user.reset_code_expires > datetime.utcnow():
        user.reset_code = None
        user.reset_code_expires = None
        db.session.commit()
        return {'success': True}, 200

    return {'error': 'Código inválido o expirado'}, 400

@auth.route('/google-login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))

    resp = google.get('/oauth2/v1/userinfo')
    if resp.ok:
        google_info = resp.json()
        user = User.query.filter_by(google_id=google_info['id']).first()

        if not user:
            user = User(
                username=google_info['email'].split('@')[0],
                email=google_info['email'],
                google_id=google_info['id']
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash('¡Inicio de sesión con Google exitoso!', 'success')
        return redirect(url_for('routes.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('routes.index'))