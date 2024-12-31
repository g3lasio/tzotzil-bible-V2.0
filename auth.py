"""
Sistema de autenticación simplificado
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, LoginManager
from models import User
from flask_mail import Message
from extensions import mail # Assuming mail is configured in extensions.py


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
            token = user.get_reset_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message('Restablecer Contraseña',
                      sender='noreply@biblereader.com',
                      recipients=[user.email])
            msg.html = render_template('auth/email/reset_password.html',
                                   user=user,
                                   reset_url=reset_url)
            try:
                mail.send(msg)
                flash('Se han enviado las instrucciones a tu email.', 'success')
            except Exception as e:
                logger.error(f"Error enviando email: {str(e)}")
                flash('Error al enviar el email. Por favor intenta más tarde.', 'error')
            return redirect(url_for('auth.login'))
        flash('Si el email existe en nuestra base de datos, recibirás instrucciones.', 'info')
    return render_template('auth/forgot_password.html')

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        user = User.verify_reset_token(token)
        if not user:
            flash('El enlace es inválido o ha expirado', 'error')
            return redirect(url_for('auth.forgot_password'))
            
        if request.method == 'POST':
            password = request.form.get('password')
            if password:
                user.set_password(password)
                db.session.commit()
                flash('Tu contraseña ha sido actualizada', 'success')
                return redirect(url_for('auth.login'))
                
        return render_template('auth/reset_password.html')
    except Exception as e:
        logger.error(f"Error en reset_password: {str(e)}")
        flash('Ocurrió un error al restablecer la contraseña', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    """Maneja el cierre de sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('routes.index'))