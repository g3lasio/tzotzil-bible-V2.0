
"""
Sistema de autenticación simplificado
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, LoginManager
from models import User

def init_login_manager(app):
    """Initialize the login manager for the application"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
    login_manager.login_message_category = 'info'
    return login_manager

import logging

# Configuración del logger
logger = logging.getLogger(__name__)

# Inicialización de login_manager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

# Crear Blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios"""
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
                flash('¡Inicio de sesión exitoso!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('routes.index'))

            flash('Usuario o contraseña inválidos', 'error')
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            flash('Error al intentar iniciar sesión', 'error')

    return render_template('auth/login.html')

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Las instrucciones para restablecer la contraseña han sido enviadas a tu email.', 'info')
            return redirect(url_for('auth.login'))
        flash('Email no encontrado', 'error')
    return render_template('auth/forgot_password.html')

@auth.route('/logout')
@login_required
def logout():
    """Maneja el cierre de sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('routes.index'))
