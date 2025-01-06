import logging
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from threading import Thread, Lock
from sqlalchemy import text
from extensions import db
from flask import current_app

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMonitor:
    """Monitor simplificado de estado de la base de datos"""

    def __init__(self, app=None):
        self.app = app
        self.is_running = False
        self.monitor_thread = None
        self.status_lock = Lock()
        self._reset_status()

        if app is not None:
            self.init_app(app)

    def _reset_status(self):
        """Reinicia el estado del monitor"""
        self.status = {
            'is_healthy': False,
            'last_check': None,
            'error_message': None,
            'connections': 0,
            'last_successful_query': None,
            'recovery_attempts': 0,
            'max_recovery_attempts': 3
        }

    def init_app(self, app):
        """Inicializa el monitor con una instancia de Flask"""
        self.app = app
        self._reset_status()

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['db_monitor'] = self

    def start(self):
        """Inicia el monitor en un thread separado"""
        if self.is_running:
            return

        if not self.app:
            logger.info("Monitor iniciado sin aplicación Flask, esperando inicialización posterior")
            return

        try:
            self.is_running = True
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Monitor de base de datos iniciado")

        except Exception as e:
            logger.error(f"Error iniciando monitor: {str(e)}")
            self.is_running = False

    def stop(self):
        """Detiene el monitor"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
            logger.info("Monitor de base de datos detenido")

    def _monitor_loop(self):
        """Loop principal del monitor"""
        while self.is_running:
            try:
                if self.app:
                    with self.app.app_context():
                        self.check_database_health()
                        if not self.status['is_healthy']:
                            self._attempt_recovery()
                else:
                    logger.warning("Monitor ejecutándose sin aplicación Flask")

                # Esperar 30 segundos entre verificaciones
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error en monitor loop: {str(e)}")
                time.sleep(60)  # Esperar más tiempo si hay error

    def check_database_health(self) -> bool:
        """Verifica el estado de la base de datos"""
        try:
            # Ejecutar una consulta simple de verificación
            db.session.execute(text('SELECT 1')).scalar()

            with self.status_lock:
                self.status.update({
                    'is_healthy': True,
                    'last_check': datetime.utcnow(),
                    'error_message': None,
                    'last_successful_query': datetime.utcnow()
                })

            return True

        except Exception as e:
            error_msg = f"Error de base de datos: {str(e)}"
            logger.error(error_msg)

            with self.status_lock:
                self.status.update({
                    'is_healthy': False,
                    'last_check': datetime.utcnow(),
                    'error_message': error_msg
                })

            return False

    def _attempt_recovery(self) -> bool:
        """Intenta recuperar la conexión a la base de datos"""
        if self.status['recovery_attempts'] >= self.status['max_recovery_attempts']:
            logger.error("Máximo número de intentos de recuperación alcanzado")
            return False

        try:
            logger.info("Intentando recuperar conexión a base de datos...")
            self.status['recovery_attempts'] += 1

            # Intentar reconectar
            db.session.remove()
            db.engine.dispose()

            # Verificar conexión
            return self.check_database_health()

        except Exception as e:
            logger.error(f"Error en intento de recuperación: {str(e)}")
            return False

    def get_status(self) -> Dict:
        """Retorna el estado actual del monitor"""
        with self.status_lock:
            return self.status.copy()

    def get_health_metrics(self) -> Dict:
        """Obtiene métricas detalladas de salud"""
        try:
            with self.app.app_context():
                result = db.session.execute(text("""
                    SELECT 
                        pg_database_size(current_database()) as db_size,
                        pg_size_pretty(pg_database_size(current_database())) as pretty_size,
                        (SELECT count(*) FROM pg_stat_activity) as total_connections,
                        (SELECT state, count(*) FROM pg_stat_activity GROUP BY state) as connection_states
                """))
                metrics = result.fetchone()

                return {
                    'database_size': metrics[1],
                    'total_connections': metrics[2],
                    'connection_states': metrics[3],
                    'last_check': datetime.utcnow(),
                    'uptime': self._get_uptime()
                }
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {str(e)}")
            return {}

    def _get_uptime(self) -> Optional[timedelta]:
        """Calcula el tiempo de actividad del monitor"""
        if not self.status['last_successful_query']:
            return None
        return datetime.utcnow() - self.status['last_successful_query']

# Instancia global del monitor
db_monitor = DatabaseMonitor()