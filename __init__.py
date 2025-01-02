
import os
from flask import Flask, session, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_cors import CORS
from models import User, db
from extensions import init_extensions

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-nevin')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bible_app.db'
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    init_extensions(app)
    app.run(host='0.0.0.0', port=8080, debug=True)
