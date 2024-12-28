import logging
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from threading import Thread, Lock
from sqlalchemy import text
from extensions import db
from flask import current_app, g

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
        self.status = {
            'is_healthy': False,
            'last_check': None,
            'error_message': None,
            'connections': 0,
            'last_successful_query': None,
            'recovery_attempts': 0,
            'max_recovery_attempts': 3
        }

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Inicializa el monitor con una instancia de Flask"""
        self.app = app
        app.teardown_appcontext(self.cleanup_context)

    def cleanup_context(self, exception=None):
        """Limpia el contexto de la aplicación"""
        try:
            if hasattr(g, 'db_session'):
                g.db_session.close()
                delattr(g, 'db_session')
        except Exception as e:
            logger.error(f"Error limpiando contexto: {str(e)}")

    def start(self):
        """Inicia el monitor en un thread separado"""
        if self.is_running:
            return

        if not self.app:
            logger.error("No se puede iniciar el monitor sin una aplicación Flask")
            return

        try:
            # Verificación inicial de la base de datos
            with self.app.app_context():
                self.check_database_health()
                if not self.status['is_healthy']:
                    logger.error(f"No se puede iniciar el monitor: {self.status['error_message']}")
                    self._attempt_recovery()
                    if not self.status['is_healthy']:
                        return

                self.is_running = True
                self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
                self.monitor_thread.start()
                logger.info("Monitor de base de datos iniciado")

        except Exception as e:
            logger.error(f"Error iniciando monitor: {str(e)}")

    def stop(self):
        """Detiene el monitor"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

    def _monitor_loop(self):
        """Loop principal del monitor"""
        while self.is_running:
            try:
                with self.app.app_context():
                    self.check_database_health()
                    if not self.status['is_healthy']:
                        self._attempt_recovery()

                # Esperar 30 segundos entre verificaciones
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error en monitor loop: {str(e)}")
                time.sleep(60)  # Esperar más tiempo si hay error

    def _attempt_recovery(self) -> bool:
        """Intenta recuperar la conexión a la base de datos"""
        if self.status['recovery_attempts'] >= self.status['max_recovery_attempts']:
            logger.error("Máximo número de intentos de recuperación alcanzado")
            return False

        try:
            logger.info("Intentando recuperar conexión a base de datos...")
            self.status['recovery_attempts'] += 1

            # Intentar reconectar
            with self.app.app_context():
                db.session.remove()
                db.engine.dispose()

                # Verificar conexión
                self.check_database_health()

                if self.status['is_healthy']:
                    logger.info("Recuperación exitosa")
                    self.status['recovery_attempts'] = 0
                    return True

        except Exception as e:
            logger.error(f"Error en intento de recuperación: {str(e)}")

        return False

    def check_database_health(self) -> bool:
        """Verifica el estado de la base de datos"""
        try:
            # Ejecutar una consulta simple de verificación
            db.session.execute(text('SELECT 1')).scalar()

            # Verificar número de conexiones y otros estados
            result = db.session.execute(text("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE application_name = 'tzotzil_bible'
            """))

            connections = result.scalar()

            # Verificar memoria y otros recursos
            result = db.session.execute(text("""
                SELECT pg_database_size(current_database()) as db_size,
                       pg_size_pretty(pg_database_size(current_database())) as pretty_size
            """))
            db_stats = result.fetchone()

            with self.status_lock:
                self.status.update({
                    'is_healthy': True,
                    'last_check': datetime.utcnow(),
                    'error_message': None,
                    'connections': connections,
                    'database_size': db_stats[1],
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
                    'error_message': error_msg,
                    'connections': 0
                })

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