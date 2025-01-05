
import os
import logging
import psutil
from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_system_health():
    status = {
        'memory_usage': psutil.virtual_memory().percent,
        'cpu_usage': psutil.cpu_percent(),
        'disk_usage': psutil.disk_usage('/').percent,
        'database': False,
        'faiss_indices': False
    }
    
    try:
        db = DatabaseManager()
        status['database'] = db.check_health()
        
        faiss_path = 'nevin_knowledge'
        if os.path.exists(faiss_path) and len(os.listdir(faiss_path)) > 0:
            status['faiss_indices'] = True
            
        return status
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return status

if __name__ == "__main__":
    print(check_system_health())


import logging
from database import DatabaseManager
from Nevin_AI.knowledge_base_manager import KnowledgeBaseManager
from test_openai_connection import test_openai_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_system():
    status = {
        'database': False,
        'faiss': False,
        'openai': False,
        'cache': False
    }
    
    try:
        # Verificar base de datos
        db_manager = DatabaseManager()
        db_health = db_manager.check_health()
        status['database'] = db_health['is_healthy']
        if not status['database']:
            logger.error(f"Problema con la base de datos: {db_health['error']}")
            
        # Verificar caché
        status['cache'] = db_manager.verify_cache()
        
        # Verificar FAISS
        kb_manager = KnowledgeBaseManager()
        status['faiss'] = kb_manager.initialize()
        
        # Verificar OpenAI
        status['openai'] = test_openai_connection()
        
        return all(status.values()), status
        
    except Exception as e:
        logger.critical(f"Error crítico en verificación del sistema: {str(e)}")
        return False, status
        
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
