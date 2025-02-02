import json
import logging

logger = logging.getLogger(__name__) # Assuming a logger is already configured


def _load_doctrinal_validation(self) -> Dict:
        """Carga el archivo de validación doctrinal."""
        try:
            path = 'Nevin_AI/data/validacion_doctrinal.json'
            logger.info(f"Intentando cargar validación doctrinal desde: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Validación doctrinal cargada exitosamente: {len(data.get('categories', []))} categorías")
                return data
        except FileNotFoundError:
            logger.error(f"Archivo de validación doctrinal no encontrado en: {path}")
            return {} # Return an empty dictionary to handle the error gracefully
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar el archivo JSON de validación doctrinal en: {path}")
            return {} # Return an empty dictionary to handle the error gracefully
        except Exception as e:
            logger.exception(f"Error inesperado al cargar la validación doctrinal: {e}")
            return {} # Return an empty dictionary to handle the error gracefully