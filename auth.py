"""
Sistema de autenticación simplificado
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import User, db
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

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

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """Maneja el registro de nuevos usuarios"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            if not all([username, email, password]):
                flash('Todos los campos son requeridos', 'error')
                return render_template('auth/signup.html')

            # Verificar si el usuario ya existe
            if User.query.filter((User.username == username) | 
                               (User.email == email)).first():
                flash('El usuario o email ya está registrado', 'error')
                return render_template('auth/signup.html')

            # Crear nuevo usuario
            user = User(username=username, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            # Iniciar sesión automáticamente
            login_user(user)
            flash('¡Registro exitoso!', 'success')
            return redirect(url_for('routes.index'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en registro: {str(e)}")
            flash('Error al crear el usuario', 'error')

    return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
def logout():
    """Maneja el cierre de sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('routes.index'))