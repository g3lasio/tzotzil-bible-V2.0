import time
import subprocess
import logging
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_process.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_import_process():
    while True:
        try:
            logging.info(f"Iniciando proceso de importación: {datetime.now()}")
            
            # Ejecutar el proceso de importación
            result = subprocess.run(
                ['python', 'import_theological_content.py'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logging.error(f"Error en la importación: {result.stderr}")
            else:
                logging.info("Importación completada exitosamente")
            
            # Esperar 5 minutos antes del siguiente intento
            logging.info("Esperando 5 minutos antes del siguiente ciclo...")
            time.sleep(300)
            
        except Exception as e:
            logging.error(f"Error inesperado: {str(e)}")
            logging.info("Reintentando en 1 minuto...")
            time.sleep(60)

if __name__ == "__main__":
    logging.info("Iniciando proceso automático de importación")
    run_import_process()
