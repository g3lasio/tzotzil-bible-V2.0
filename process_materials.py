
import os
import logging
from pathlib import Path
from document_processor import DocumentProcessor
from database import get_db
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Configura la base de datos para el contenido teológico."""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS theological_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            source TEXT,
            source_type TEXT,
            page_number INTEGER,
            chunk_number INTEGER,
            embedding_id TEXT
        )
    """)
    db.commit()

def process_all_materials():
    """Procesa todos los materiales (PDFs y JSONs) y los almacena en la base de datos."""
    processor = DocumentProcessor()
    db = get_db()
    cursor = db.cursor()
    
    setup_database()
    
    # Procesar PDFs teológicos
    pdf_folders = ['Teologico', 'Theology']
    for folder in pdf_folders:
        if not os.path.exists(folder):
            logger.warning(f"Carpeta {folder} no encontrada")
            continue
            
        for pdf_file in Path(folder).glob('*.pdf'):
            logger.info(f"Procesando PDF: {pdf_file}")
            documents = processor.process_pdf(str(pdf_file))
            
            for doc in documents:
                try:
                    cursor.execute(
                        """INSERT INTO theological_content 
                           (title, content, source, source_type, page_number, chunk_number)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (doc['title'], 
                         doc['content'], 
                         doc['metadata']['source'],
                         doc['metadata']['type'],
                         doc['metadata']['page'],
                         doc['metadata']['chunk'])
                    )
                except sqlite3.Error as e:
                    logger.error(f"Error insertando documento: {e}")
            
            db.commit()
            logger.info(f"PDF {pdf_file} procesado exitosamente")
    
    # Procesar JSONs de EGW
    egw_folder = 'EGW BOOKS'
    if os.path.exists(egw_folder):
        for json_file in Path(egw_folder).glob('*.json'):
            logger.info(f"Procesando libro EGW: {json_file}")
            documents = processor.process_jsonl(str(json_file))
            
            for doc in documents:
                try:
                    cursor.execute(
                        """INSERT INTO theological_content 
                           (title, content, source, source_type, page_number, chunk_number)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (doc['title'], 
                         doc['content'], 
                         doc['metadata']['source'],
                         doc['metadata']['type'],
                         doc['metadata']['page'],
                         doc['metadata']['chunk'])
                    )
                except sqlite3.Error as e:
                    logger.error(f"Error insertando documento: {e}")
            
            db.commit()
            logger.info(f"Libro {json_file} procesado exitosamente")

if __name__ == "__main__":
    process_all_materials()
