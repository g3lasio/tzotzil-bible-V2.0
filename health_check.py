
import logging
from flask import Flask
from extensions import db, init_extensions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_health_check():
    """Health check simplificado."""
    try:
        app = Flask(__name__)
        init_extensions(app)
        
        with app.app_context():
            db.session.execute(text('SELECT 1')).scalar()
            logger.info("Verificación de salud completada")
            return True
            
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return False

if __name__ == "__main__":
    run_health_check()
