
import logging
from flask import Flask
from extensions import db, init_extensions
from database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_health_check():
    """Ejecuta verificación completa del sistema."""
    try:
        app = Flask(__name__)
        init_extensions(app)
        
        with app.app_context():
            # Verificar conexión básica
            db.session.execute(text('SELECT 1')).scalar()
            
            # Verificar tablas esenciales
            tables = ['bibleverse', 'users', 'promise']
            for table in tables:
                result = db.session.execute(
                    text(f"SELECT EXISTS (SELECT 1 FROM {table} LIMIT 1)")
                ).scalar()
                if not result:
                    logger.warning(f"Tabla {table} está vacía")
                    
            logger.info("Verificación de salud completada exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"Error en verificación de salud: {str(e)}")
        return False

if __name__ == "__main__":
    run_health_check()
