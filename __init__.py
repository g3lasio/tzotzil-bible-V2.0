
import os
from flask import Flask, session, request, redirect, url_for, render_template
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-nevin')
CORS(app)

USERS = {
    'admin': 'password123'  # En producción usar hash
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if USERS.get(request.form['username']) == request.form['password']:
            session['user'] = request.form['username']
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['user'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
