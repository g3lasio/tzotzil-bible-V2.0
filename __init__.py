
"""
Inicialización principal de la aplicación
"""
import os
import logging
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
cors = CORS()
login_manager = LoginManager()
mail = Mail()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración base
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-nevin'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///bible_app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    from auth import auth
    from routes import routes
    from nevin_routes import nevin_bp
    
    app.register_blueprint(auth)
    app.register_blueprint(routes)
    app.register_blueprint(nevin_bp, url_prefix='/nevin')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
