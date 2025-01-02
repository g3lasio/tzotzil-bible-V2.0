
import os
from flask import Flask, session, request, redirect, url_for, render_template, jsonify
from flask_cors import CORS
from extensions import init_extensions

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-nevin')
CORS(app)

def get_replit_user():
    if request.headers.get('X-Replit-User-Id'):
        return {
            'id': request.headers.get('X-Replit-User-Id'),
            'name': request.headers.get('X-Replit-User-Name'),
            'bio': request.headers.get('X-Replit-User-Bio'),
            'profile_image': request.headers.get('X-Replit-User-Profile-Image')
        }
    return None

@app.before_request
def check_auth():
    if not request.path.startswith('/static'):
        user = get_replit_user()
        if not user and request.path != '/login':
            return redirect('/login')
        session['user'] = user

@app.route('/login')
def login():
    if get_replit_user():
        return redirect(url_for('index'))
    return render_template('auth/login.html')

@app.route('/')
def index():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('index.html', user=user)

@app.route('/user')
def get_user():
    return jsonify(session.get('user'))

if __name__ == '__main__':
    init_extensions(app)
    app.run(host='0.0.0.0', port=8080, debug=True)
