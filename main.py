
import logging
import time
from typing import Tuple
from sqlalchemy import text
from extensions import db
from database import db_manager
from cache_manager import cache_manager
from db_monitor import db_monitor

def verify_critical_services(app) -> Tuple[bool, str]:
    """Verifica el estado de los servicios críticos."""
    try:
        with app.app_context():
            # 1. Verificar base de datos
            try:
                db.session.execute(text('SELECT 1'))
                logger.info("Conexión a base de datos verificada")
            except Exception as e:
                return False, f"Error en base de datos: {str(e)}"

            # 2. Verificar monitor de base de datos
            if not db_monitor.is_running:
                return False, "Monitor de base de datos no está ejecutándose"
            logger.info("Monitor de base de datos verificado")

            return True, "Todos los servicios críticos funcionando correctamente"
    except Exception as e:
        return False, f"Error verificando servicios: {str(e)}"

"""
Módulo principal para inicialización y gestión de la aplicación
"""
import logging
import os
import time
import socket
import psutil
import signal
import sys
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from database import db_manager
from cache_manager import cache_manager
from extensions import db
from db_monitor import db_monitor
from sqlalchemy.sql import text
from app import create_app

# Configuración de logging mejorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def verify_port_availability(port: int, retries: int = 3, wait_time: int = 2) -> bool:
    """Verifica si un puerto está disponible con reintentos"""
    for attempt in range(retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('0.0.0.0', port))
                if result != 0:  # Puerto está libre
                    return True
                logger.warning(f"Puerto {port} ocupado, intento {attempt + 1}/{retries}")
                time.sleep(wait_time)
        except Exception as e:
            logger.error(f"Error verificando puerto {port}: {e}")
    return False

def force_kill_process(pid):
    """Fuerza el cierre de un proceso"""
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        if psutil.pid_exists(pid):
            os.kill(pid, signal.SIGKILL)
    except Exception as e:
        logger.error(f"Error matando proceso {pid}: {e}")

def cleanup_resources(app=None):
    """Limpia recursos y conexiones antes de iniciar el servidor."""
    try:
        if app:
            with app.app_context():
                # Limpiar conexiones de base de datos
                if hasattr(db, 'session'):
                    db.session.remove()
                if hasattr(db, 'engine'):
                    db.engine.dispose()
                logger.info("Conexiones de base de datos limpiadas")

        # Buscar y cerrar procesos que usen los puertos necesarios
        port = int(os.environ.get('PORT', 5000))
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.connections():
                        if hasattr(conn, 'laddr') and conn.laddr.port == port:
                            logger.warning(f"Forzando cierre de proceso {proc.pid} en puerto {port}")
                            force_kill_process(proc.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not verify_port_availability(port):
                logger.error(f"No se pudo liberar el puerto {port}")
                return False

        except Exception as e:
            logger.error(f"Error limpiando puerto {port}: {e}")
            return False

        logger.info("Limpieza de recursos completada exitosamente")
        return True

    except Exception as e:
        logger.error(f"Error fatal en limpieza de recursos: {e}")
        return False

def verify_critical_services(app) -> Tuple[bool, str]:
    """Verifica el estado de los servicios críticos."""
    try:
        with app.app_context():
            # 1. Verificar base de datos
            try:
                db.session.execute(text('SELECT 1'))
                logger.info("Conexión a base de datos verificada")
            except Exception as e:
                return False, f"Error en base de datos: {str(e)}"

            # 2. Verificar caché
            if not cache_manager.ping():
                return False, "Error en sistema de caché"
            logger.info("Sistema de caché verificado")

            # 3. Verificar monitor de base de datos
            if not db_monitor.is_running:
                return False, "Monitor de base de datos no está ejecutándose"
            logger.info("Monitor de base de datos verificado")

            return True, "Todos los servicios críticos funcionando correctamente"
    except Exception as e:
        return False, f"Error verificando servicios: {str(e)}"

def start_server(app) -> None:
    """Inicia el servidor con manejo mejorado de errores y recuperación."""
    try:
        # Verificar servicios críticos antes de iniciar
        services_ok, service_msg = verify_critical_services(app)
        if not services_ok:
            raise Exception(f"Servicios críticos no disponibles: {service_msg}")
        logger.info("Verificación de servicios críticos completada")

        # Limpiar recursos
        logger.info("Iniciando limpieza de recursos...")
        if not cleanup_resources(app):
            raise Exception("No se pudieron limpiar los recursos necesarios")

        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Verificando disponibilidad del puerto {port}...")

        if not verify_port_availability(port):
            raise Exception(f"Puerto {port} no disponible después de intentos de limpieza")

        # Configurar manejadores de señales
        def signal_handler(signum, frame):
            logger.info(f"Señal {signum} recibida, iniciando apagado seguro...")
            cleanup_resources(app)
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        # Configuración del servidor
        server_options = {
            'host': '0.0.0.0',
            'port': port,
            'threaded': True,
            'use_reloader': False,
            'debug': False  # Desactivar debug mode para producción
        }

        logger.info(f"Iniciando servidor en puerto {port}")
        app.run(**server_options)

    except Exception as e:
        logger.error(f"Error fatal iniciando el servidor: {str(e)}")
        cleanup_resources(app)
        sys.exit(1)

if __name__ == "__main__":
    try:
        logger.info("=== Iniciando proceso de arranque del servidor ===")

        # 1. Crear aplicación Flask
        logger.info("Creando aplicación Flask...")
        app = create_app()
        if not app:
            raise Exception("No se pudo crear la aplicación Flask")
        logger.info("Aplicación Flask creada exitosamente")

        # 2. Verificar servicios críticos
        logger.info("Verificando servicios críticos...")
        services_ok, service_msg = verify_critical_services(app)
        if not services_ok:
            raise Exception(f"Error en servicios críticos: {service_msg}")
        logger.info("Servicios críticos verificados correctamente")

        # 3. Iniciar monitor de base de datos
        if not db_monitor.is_running:
            db_monitor.start()
            logger.info("Monitor de base de datos iniciado")

        # 4. Iniciar servidor
        logger.info("=== Iniciando servidor ===")
        start_server(app)

    except Exception as e:
        logger.error("=== ERROR FATAL EN ARRANQUE DEL SERVIDOR ===")
        logger.error(f"Error detallado: {str(e)}")
        sys.exit(1)