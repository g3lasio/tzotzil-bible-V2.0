from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User, NevinAccess, db
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from functools import wraps
import logging
import os
import re

# Configuración inicial
auth = Blueprint('auth', __name__)
login_manager = LoginManager()
logger = logging.getLogger(__name__)
serializer = URLSafeTimedSerializer(
    os.environ.get('FLASK_SECRET_KEY', 'default-key'))


# Funciones de utilidad para validación
def validate_password(password):
    """
    Valida que la contraseña cumpla con requisitos mínimos de seguridad
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    return True, None


def validate_email(email):
    """
    Valida formato de email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    return True, None


# Decoradores personalizados
def nevin_access_required(f):
    """
    Decorador para proteger rutas que requieren acceso a Nevin
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        has_access, message = check_monthly_access(current_user.id)
        if not has_access:
            flash(message, 'error')
            return redirect(url_for('routes.index'))

        return f(*args, **kwargs)

    return decorated_function


@auth.route('/init-db', methods=['GET'])
def init_database():
    try:
        # Inicializar la base de datos
        db.create_all()

        # Crear usuario admin inicial
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin',
                              email='admin@test.com',
                              first_name='Admin',
                              last_name='User',
                              is_premium=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

            return "Base de datos inicializada y usuario admin creado exitosamente"
    except Exception as e:
        return f"Error: {str(e)}"


@auth.route('/check-db', methods=['GET'])
def check_database():
    try:
        # Contar usuarios
        user_count = User.query.count()

        # Verificar tablas
        tables_info = {
            'users_count':
            user_count,
            'users_list': [{
                'username': user.username,
                'email': user.email
            } for user in User.query.all()]
        }

        return str(tables_info)
    except Exception as e:
        return f"Error verificando base de datos: {str(e)}"


# Configuración de Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def init_login_manager(app):
    """
    Inicializa Flask-Login con la aplicación
    """
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'


# Funciones de gestión de usuarios
def init_db_user():
    """
    Crea el usuario admin inicial si no existe ningún usuario
    """
    try:
        if User.query.count() == 0:
            user = User(username='admin',
                        email='admin@test.com',
                        is_premium=True,
                        first_name='Admin',
                        last_name='System')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            logger.info("Usuario admin creado exitosamente")
    except Exception as e:
        logger.error(f"Error creando usuario inicial: {str(e)}")


def check_monthly_access(user_id):
    """
    Verifica si el usuario tiene acceso gratuito disponible este mes
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Usuario no encontrado"

        if user.is_premium:
            return True, "Usuario premium"

        start_of_month = datetime.utcnow().replace(day=1,
                                                   hour=0,
                                                   minute=0,
                                                   second=0)
        days_used = NevinAccess.query.filter(
            NevinAccess.user_id == user_id, NevinAccess.created_at
            >= start_of_month).count()

        if days_used >= 3:
            return False, "Has alcanzado el límite de 3 días este mes"

        if days_used == 0:
            new_access = NevinAccess(user_id=user_id,
                                     access_until=datetime.utcnow() +
                                     timedelta(days=1))
            db.session.add(new_access)
            db.session.commit()

        return True, "Acceso concedido"

    except Exception as e:
        logger.error(f"Error verificando acceso mensual: {str(e)}")
        return False, "Error verificando acceso"


# Rutas de autenticación
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Maneja el inicio de sesión de usuarios
    """
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember')

            user = User.query.filter((User.username == username)
                                     | (User.email == username)).first()

            if '@' in username:
                valid_email, msg = validate_email(username)
                if not valid_email:
                    flash(msg, 'error')
                    return render_template('auth/login.html', error=msg)

            if user and user.check_password(password):
                login_user(user, remember=bool(remember))
                next_page = request.args.get('next')
                flash('¡Inicio de sesión exitoso!', 'success')
                return redirect(next_page or url_for('routes.index'))

            flash('Usuario o contraseña inválidos', 'error')
            return render_template('auth/login.html',
                                   error='Usuario o contraseña inválidos')

        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            flash('Error al intentar iniciar sesión', 'error')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


# Modificar la ruta de registro en auth.py


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Maneja el registro de nuevos usuarios con mejor manejo de errores y logging
    """
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    if request.method == 'POST':
        try:
            logger.info("Iniciando proceso de registro")
            form_data = request.form.to_dict(
            )  # Convertir form data a diccionario
            logger.info(f"Datos recibidos: {form_data}"
                        )  # Log de datos recibidos (sin contraseña)

            # Validaciones básicas con mensajes más específicos
            if not form_data.get('username'):
                flash('El nombre de usuario es requerido', 'error')
                return render_template('auth/signup.html', form_data=form_data)

            if not form_data.get('email'):
                flash('El email es requerido', 'error')
                return render_template('auth/signup.html', form_data=form_data)

            if not form_data.get('password'):
                flash('La contraseña es requerida', 'error')
                return render_template('auth/signup.html', form_data=form_data)

            # Validar formato de email
            valid_email, email_msg = validate_email(form_data.get('email'))
            if not valid_email:
                flash(email_msg, 'error')
                return render_template('auth/signup.html', form_data=form_data)

            # Validar contraseña
            valid_pass, pass_msg = validate_password(form_data.get('password'))
            if not valid_pass:
                flash(pass_msg, 'error')
                return render_template('auth/signup.html', form_data=form_data)

            # Verificar que las contraseñas coincidan
            if form_data.get('password') != form_data.get('confirm_password'):
                flash('Las contraseñas no coinciden', 'error')
                return render_template('auth/signup.html', form_data=form_data)

            # Verificar usuario existente
            existing_user = User.query.filter(
                (User.username == form_data.get('username'))
                | (User.email == form_data.get('email'))).first()

            if existing_user:
                flash('El usuario o email ya está registrado', 'error')
                return render_template('auth/signup.html', form_data=form_data)

            # Crear nuevo usuario
            user = User(username=form_data.get('username'),
                        email=form_data.get('email'),
                        first_name=form_data.get('first_name'),
                        last_name=form_data.get('last_name'),
                        phone=form_data.get('phone'))
            user.set_password(form_data.get('password'))

            # Intentar guardar en la base de datos
            try:
                db.session.add(user)
                db.session.commit()
                logger.info(f"Usuario creado exitosamente: {user.username}")

                # Iniciar sesión automáticamente
                login_user(user)
                flash('¡Registro exitoso!', 'success')
                return redirect(url_for('routes.index'))

            except IntegrityError as e:
                db.session.rollback()
                logger.error(
                    f"Error de integridad en la base de datos: {str(e)}")
                flash(
                    'Error al crear el usuario: el usuario o email ya existe',
                    'error')
                return render_template('auth/signup.html', form_data=form_data)

            except Exception as e:
                db.session.rollback()
                logger.error(
                    f"Error al guardar usuario en la base de datos: {str(e)}")
                flash(
                    'Error al crear el usuario. Por favor, intenta nuevamente',
                    'error')
                return render_template('auth/signup.html', form_data=form_data)

        except Exception as e:
            logger.error(f"Error general en el registro: {str(e)}")
            flash('Error en el proceso de registro', 'error')
            return render_template('auth/signup.html')

    return render_template('auth/signup.html')


@auth.route('/logout')
@login_required
def logout():
    """
    Maneja el cierre de sesión de usuarios
    """
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('routes.index'))


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Maneja el proceso de recuperación de contraseña:
    1. Usuario solicita recuperación
    2. Se envía email con token
    3. Usuario hace clic en el enlace del email
    """
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    if request.method == 'POST':
        try:
            email = request.form.get('email')
            if not email:
                flash('El email es requerido', 'error')
                return render_template('auth/forgot_password.html')

            # Validar formato de email
            valid_email, msg = validate_email(email)
            if not valid_email:
                flash(msg, 'error')
                return render_template('auth/forgot_password.html')

            user = User.query.filter_by(email=email).first()
            if user:
                # Generar y enviar email de recuperación
                token = serializer.dumps(email, salt='password-reset-salt')
                reset_url = url_for('auth.reset_password',
                                    token=token,
                                    _external=True)

                msg = Message('Recuperación de Contraseña',
                              recipients=[email],
                              html=render_template(
                                  'auth/email/reset_password.html',
                                  user=user,
                                  reset_url=reset_url))

                mail.send(msg)
                flash('Se han enviado instrucciones a tu email', 'success')
            else:
                # No revelar si el email existe
                flash(
                    'Si existe una cuenta con ese email, recibirás instrucciones',
                    'info')

            return redirect(url_for('auth.login'))

        except Exception as e:
            logger.error(f"Error en recuperación de contraseña: {str(e)}")
            flash('Error al procesar la solicitud', 'error')

    return render_template('auth/forgot_password.html')


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Maneja el reset de contraseña usando el token enviado por email
    """
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    try:
        # Verificar token (expira en 1 hora)
        email = serializer.loads(token,
                                 salt='password-reset-salt',
                                 max_age=3600)
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Enlace de recuperación inválido o expirado', 'error')
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            # Validar nueva contraseña
            valid_pass, pass_msg = validate_password(password)
            if not valid_pass:
                flash(pass_msg, 'error')
                return render_template('auth/reset_password.html')

            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('auth/reset_password.html')

            # Actualizar contraseña
            user.set_password(password)
            db.session.commit()

            flash('Tu contraseña ha sido actualizada exitosamente', 'success')
            return redirect(url_for('auth.login'))

        return render_template('auth/reset_password.html')

    except Exception as e:
        logger.error(f"Error en reset de contraseña: {str(e)}")
        flash('Enlace de recuperación inválido o expirado', 'error')
        return redirect(url_for('auth.login'))


# Funciones de gestión de acceso a Nevin
def grant_trial_access(user_id, days=3):
    """
    Otorga acceso de prueba a Nevin por un número específico de días
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Usuario no encontrado"

        # Verificar si ya tiene acceso activo
        current_access = NevinAccess.query.filter(
            NevinAccess.user_id == user_id, NevinAccess.access_until
            > datetime.utcnow()).first()

        if current_access:
            return False, "Ya tienes acceso activo"

        # Crear nuevo acceso
        new_access = NevinAccess(user_id=user_id,
                                 access_until=datetime.utcnow() +
                                 timedelta(days=days))
        db.session.add(new_access)
        db.session.commit()

        return True, "Acceso de prueba activado exitosamente"

    except Exception as e:
        logger.error(f"Error otorgando acceso de prueba: {str(e)}")
        return False, "Error al activar el acceso de prueba"


def upgrade_to_premium(user_id):
    """
    Actualiza un usuario a estado premium
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Usuario no encontrado"

        user.is_premium = True
        db.session.commit()

        return True, "Usuario actualizado a premium exitosamente"

    except Exception as e:
        logger.error(f"Error actualizando a premium: {str(e)}")
        return False, "Error en la actualización a premium"


def check_user_status(user_id):
    """
    Verifica y retorna el estado de acceso actual de un usuario
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return "Usuario no encontrado"

        if user.is_premium:
            return "Usuario Premium - Acceso completo"

        # Buscar acceso activo
        current_access = NevinAccess.query.filter(
            NevinAccess.user_id == user_id, NevinAccess.access_until
            > datetime.utcnow()).order_by(
                NevinAccess.access_until.desc()).first()

        if current_access:
            return f"Usuario Gratuito - Acceso hasta: {current_access.access_until}"

        return "Usuario Gratuito - Sin acceso activo"

    except Exception as e:
        logger.error(f"Error verificando estado: {str(e)}")
        return "Error al verificar estado"


@auth.route('/create-test-users')
def create_test_users_route():
    try:
        success, message = create_test_users()
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Error en create_test_users_route: {str(e)}")
        flash('Error creando usuarios de prueba', 'error')
        return redirect(url_for('auth.login'))


# Añadir esto al archivo auth.py


def diagnose_database_state():
    """
    Función de diagnóstico para verificar el estado de la base de datos y la configuración de usuarios.
    """
    try:
        # Verificar si las tablas existen
        with current_app.app_context():
            # Verificar la conexión a la base de datos
            db_connection = db.engine.connect()
            logger.info(
                "Conexión a la base de datos establecida correctamente")

            # Verificar las tablas existentes
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            logger.info(f"Tablas existentes: {existing_tables}")

            # Verificar el número de usuarios
            user_count = User.query.count()
            logger.info(
                f"Número de usuarios en la base de datos: {user_count}")

            # Verificar la estructura de la tabla users
            user_columns = inspector.get_columns('users')
            logger.info(
                f"Estructura de la tabla users: {[col['name'] for col in user_columns]}"
            )

            return {
                'success': True,
                'tables': existing_tables,
                'user_count': user_count,
                'user_columns': [col['name'] for col in user_columns]
            }

    except Exception as e:
        logger.error(f"Error en diagnóstico de base de datos: {str(e)}")
        return {'success': False, 'error': str(e)}


@auth.route('/diagnose', methods=['GET'])
def diagnose():
    """Ruta para ejecutar el diagnóstico"""
    result = diagnose_database_state()
    return jsonify(result)
