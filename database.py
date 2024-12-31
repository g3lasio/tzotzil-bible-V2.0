
"""
DatabaseManager - Sistema robusto de gestión de base de datos con verificación y recuperación automática
"""
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import time
import traceback
import os
from flask import g
from sqlalchemy import text, inspect
from extensions import db
from threading import Lock

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('app.log')])
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._health_status = {
            'is_healthy': False,
            'last_check': None,
            'error': None,
            'reconnection_attempts': 0,
            'last_reconnection': None,
            'initialization_complete': False
        }
        self._max_reconnection_attempts = 5
        self._reconnection_delay = 2
        self._initialization_lock = Lock()
        self._session_lock = Lock()
        logger.info("DatabaseManager inicializado")

    def get_session(self):
        """Obtiene una sesión de base de datos con manejo de errores y reconexión automática"""
        with self._session_lock:
            try:
                if not hasattr(g, 'db_session'):
                    logger.info("Inicializando nueva sesión de base de datos")
                    self._verify_database()
                    logger.info("Creando nueva sesión de base de datos...")
                    
                    for attempt in range(3):
                        try:
                            g.db_session = db.session
                            g.db_session.execute(text('SELECT 1')).scalar()
                            logger.info("Nueva sesión de base de datos creada y verificada")
                            break
                        except Exception as e:
                            logger.error(f"Intento {attempt + 1} fallido: {str(e)}")
                            if hasattr(g, 'db_session'):
                                g.db_session.remove()
                            if attempt == 2:
                                raise
                            time.sleep(2)
                return g.db_session
            except Exception as e:
                logger.error(f"Error al obtener sesión de base de datos: {str(e)}")
                logger.error(traceback.format_exc())
                if hasattr(g, 'db_session'):
                    try:
                        g.db_session.remove()
                    except Exception:
                        pass
                    delattr(g, 'db_session')
                raise

    def _verify_database(self):
        """Verifica la integridad de la base de datos"""
        try:
            inspector = inspect(db.engine)
            required_tables = ['bibleverse', 'users', 'promise']
            existing_tables = inspector.get_table_names()
            
            missing_tables = set(required_tables) - set(existing_tables)
            if missing_tables:
                logger.error(f"Tablas faltantes: {missing_tables}")
                with db.engine.connect() as conn:
                    conn.execute(text('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)'))
                    conn.execute(text('CREATE TABLE IF NOT EXISTS bibleverse (id INTEGER PRIMARY KEY)'))
                    conn.execute(text('CREATE TABLE IF NOT EXISTS promise (id INTEGER PRIMARY KEY)'))
                logger.info("Tablas base creadas")
                
        except Exception as e:
            logger.error(f"Error verificando base de datos: {str(e)}")
            raise

    def check_health(self) -> Dict[str, Any]:
        """Verifica el estado de salud de la base de datos"""
        try:
            session = self.get_session()
            session.execute(text('SELECT 1')).scalar()
            return {
                'is_healthy': True,
                'last_check': datetime.utcnow(),
                'error': None
            }
        except Exception as e:
            error_msg = f"Error en health check: {str(e)}"
            logger.error(error_msg)
            return {
                'is_healthy': False,
                'last_check': datetime.utcnow(),
                'error': error_msg
            }

# Instancia global del gestor
db_manager = DatabaseManager()

def get_db():
    """Obtiene una sesión de base de datos"""
    return db_manager.get_session()
