
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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
cors = CORS()
login_manager = LoginManager()
mail = Mail()

def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///bible_app.db')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-key-nevin'),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_pre_ping': True,
            'pool_recycle': 300
        }
    )

    if test_config:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    cors.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from auth import auth
    from routes import routes
    from nevin_routes import nevin_bp
    
    app.register_blueprint(auth)
    app.register_blueprint(routes)
    app.register_blueprint(nevin_bp, url_prefix='/nevin')
    
    with app.app_context():
        db.create_all()
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
