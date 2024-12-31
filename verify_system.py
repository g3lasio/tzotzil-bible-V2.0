
import logging
from database import DatabaseManager
from Nevin_AI.knowledge_base_manager import KnowledgeBaseManager
from test_openai_connection import test_openai_connection
from extensions import init_extensions
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_system():
    """Verificación completa del sistema"""
    try:
        # 1. Verificar base de datos
        db_manager = DatabaseManager()
        db_health = db_manager.check_health()
        if not db_health['is_healthy']:
            logger.error(f"Problema con la base de datos: {db_health['error']}")
            return False
            
        # 2. Verificar índices FAISS
        kb_manager = KnowledgeBaseManager()
        if not kb_manager.initialize():
            logger.error("Problema con los índices FAISS")
            return False
            
        # 3. Verificar OpenAI
        if not test_openai_connection():
            logger.error("Problema con la conexión a OpenAI")
            return False
            
        # 4. Verificar extensiones Flask
        app = Flask(__name__)
        if not init_extensions(app):
            logger.error("Problema inicializando extensiones Flask")
            return False

        logger.info("Verificación del sistema completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"Error en verificación del sistema: {str(e)}")
        return False

if __name__ == "__main__":
    verify_system()
