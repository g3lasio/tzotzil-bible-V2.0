
import logging
from database import DatabaseManager
from Nevin_AI.knowledge_base_manager import KnowledgeBaseManager
from test_openai_connection import test_openai_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_system():
    # Verificar base de datos
    db_manager = DatabaseManager()
    db_health = db_manager.check_health()
    if not db_health['is_healthy']:
        logger.error(f"Problema con la base de datos: {db_health['error']}")
        return False
        
    # Verificar índices FAISS
    kb_manager = KnowledgeBaseManager()
    if not kb_manager.initialize():
        logger.error("Problema con los índices FAISS")
        return False
        
    # Verificar OpenAI
    if not test_openai_connection():
        logger.error("Problema con la conexión a OpenAI")
        return False
        
    logger.info("Verificación del sistema completada exitosamente")
    return True

if __name__ == "__main__":
    verify_system()
