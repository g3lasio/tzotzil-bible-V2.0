
import faiss
import numpy as np
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.index = None
        
    def initialize(self):
        """Inicializa el índice FAISS."""
        try:
            if not self.index_path.exists():
                logger.warning(f"Ruta de índice no encontrada: {self.index_path}")
                return False
                
            self.index = faiss.read_index(str(self.index_path))
            if not self.index.is_trained:
                logger.warning("Índice no está entrenado")
                return False
                
            logger.info(f"Índice FAISS inicializado exitosamente: {self.index_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando índice FAISS: {str(e)}")
            return False
            
    def search(self, query_vector: np.ndarray, top_k: int = 5):
        """Realiza búsqueda en el índice."""
        if self.index is None:
            return None, None
            
        try:
            return self.index.search(query_vector, top_k)
        except Exception as e:
            logger.error(f"Error en búsqueda FAISS: {str(e)}")
            return None, None
