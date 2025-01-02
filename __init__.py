
import os
from flask import Flask, session, request, redirect, url_for, render_template, jsonify, flash
from flask_cors import CORS
from extensions import init_extensions, db
from models import User
from flask_login import LoginManager, login_user, current_user

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

def get_replit_user():
    if request.headers.get('X-Replit-User-Id'):
        return {
            'id': request.headers.get('X-Replit-User-Id'),
            'name': request.headers.get('X-Replit-User-Name'),
            'bio': request.headers.get('X-Replit-User-Bio'),
            'profile_image': request.headers.get('X-Replit-User-Profile-Image')
        }
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            return redirect(url_for('index'))
        flash('Email o contraseña incorrectos', 'error')
        
    replit_user = get_replit_user()
    if replit_user:
        user = User.query.filter_by(replit_id=replit_user['id']).first()
        if not user:
            user = User(
                username=replit_user['name'],
                email=f"{replit_user['id']}@replit.user",
                replit_id=replit_user['id']
            )
            db.session.add(user)
            db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
        
    return render_template('auth/login.html')

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    init_extensions(app)
    app.run(host='0.0.0.0', port=8080, debug=True)
