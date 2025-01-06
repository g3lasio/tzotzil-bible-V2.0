import os
from flask import Flask, jsonify
from flask_cors import CORS
from database import db_manager
from routes import init_routes
from extensions import init_extensions
import logging

def create_app():
    app = Flask(__name__)

    # Configuración CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://sistema-nevin.replit.app", "https://tzotzil-bible-reader.replit.app"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configurar la aplicación
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev_key_only_for_development")

    # Importar y registrar manejadores de errores
    from error_handlers import register_error_handlers
    register_error_handlers(app)

    # Inicializar extensiones
    init_extensions(app)

    # Inicializar rutas
    init_routes(app)

    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy"})

    return app

# Para ejecución directa del archivo
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)