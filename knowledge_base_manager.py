import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import faiss
import numpy as np
from openai import OpenAI
from document_processor import DocumentProcessor

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """Gestor de la base de conocimientos para Nevin usando FAISS."""

    def __init__(self, knowledge_dir: str = "nevin_knowledge"):
        """
        Inicializa el gestor de la base de conocimientos.
        
        Args:
            knowledge_dir: Directorio que contiene los archivos FAISS
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.document_processor = DocumentProcessor()
        self.faiss_indexes = {}
        self._load_faiss_indexes()
        logger.info(f"Gestor de base de conocimientos inicializado desde: {knowledge_dir}")

    def _load_faiss_indexes(self):
        """Carga todos los índices FAISS del directorio de conocimiento."""
        try:
            if not self.knowledge_dir.exists():
                raise ValueError(f"Directorio {self.knowledge_dir} no existe")

            # Cargar todos los archivos .faiss
            faiss_files = list(self.knowledge_dir.glob("*.faiss"))
            logger.info(f"Encontrados {len(faiss_files)} archivos FAISS")

            for faiss_file in faiss_files:
                try:
                    index = faiss.read_index(str(faiss_file))
                    self.faiss_indexes[faiss_file.stem] = index
                    logger.info(f"Índice FAISS cargado: {faiss_file.name}")
                except Exception as e:
                    logger.error(f"Error cargando índice {faiss_file}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error cargando índices FAISS: {e}")
            raise

    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca en todos los índices FAISS cargados usando el texto de la consulta.
        
        Args:
            query: Texto de la consulta
            top_k: Número de resultados a retornar por índice
            
        Returns:
            Lista combinada de resultados más relevantes
        """
        try:
            # Generar embedding para la consulta
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                logger.error("No se pudo generar embedding para la consulta")
                return []

            all_results = []
            query_vector = np.array([query_embedding]).astype('float32')

            for index_name, index in self.faiss_indexes.items():
                try:
                    # Realizar búsqueda en el índice actual
                    D, I = index.search(query_vector, top_k)
                    
                    # Procesar resultados
                    for distance, idx in zip(D[0], I[0]):
                        if idx != -1:  # -1 indica resultado no válido
                            score = 1.0 / (1.0 + distance)  # Convertir distancia a score
                            content = self._get_content_by_id(index_name, idx)
                            if content:
                                result = {
                                    'content': content,
                                    'metadata': {
                                        'source': index_name,
                                        'index_id': int(idx),
                                        'type': self._get_content_type(index_name)
                                    },
                                    'score': float(score)
                                }
                                all_results.append(result)
                            
                except Exception as e:
                    logger.error(f"Error buscando en índice {index_name}: {e}")
                    continue

            # Ordenar resultados por score y tomar los top_k mejores
            sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=True)
            return sorted_results[:top_k]

        except Exception as e:
            logger.error(f"Error en búsqueda de conocimientos: {e}")
            return []

    def _get_content_by_id(self, index_name: str, idx: int) -> Optional[str]:
        """
        Obtiene el contenido asociado a un ID en un índice específico.
        """
        try:
            content_path = self.knowledge_dir / f"{index_name}_content.json"
            if not content_path.exists():
                logger.error(f"Archivo de contenido no encontrado: {content_path}")
                return None

            with open(content_path, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
                return content_data.get(str(idx))

        except Exception as e:
            logger.error(f"Error obteniendo contenido para {index_name}, ID {idx}: {e}")
            return None

    def _get_content_type(self, index_name: str) -> str:
        """
        Determina el tipo de contenido basado en el nombre del índice.
        """
        if 'bible' in index_name.lower():
            return 'bible'
        elif 'egw' in index_name.lower():
            return 'egw'
        elif 'theological' in index_name.lower():
            return 'theological'
        return 'unknown'

    def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Genera embedding para un texto usando OpenAI.
        
        Args:
            text: Texto para generar embedding
        
        Returns:
            Array numpy con el embedding
        """
        try:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            if response.data and response.data[0].embedding:
                return np.array(response.data[0].embedding, dtype=np.float32)
            return None
            
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return None

    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca en la base de conocimientos.
        
        Args:
            query: Consulta a buscar
            top_k: Número de resultados a retornar
            
        Returns:
            Lista de resultados más relevantes
        """
        try:
            # Generar embedding para la consulta
            query_embedding = self._generate_embedding(query)
            
            if not query_embedding:
                logger.warning("No se pudo generar embedding para la consulta")
                return []
            
            # Realizar búsqueda en Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return results['matches'] if 'matches' in results else []
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []

def main():
    """Función principal para pruebas."""
    kb_manager = KnowledgeBaseManager()
    logger.info("Gestor de base de conocimientos inicializado")
    
    # Aquí se pueden agregar pruebas o procesamiento por lotes
    
if __name__ == "__main__":
    main()
