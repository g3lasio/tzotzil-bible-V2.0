
import sqlite3
import json
import logging
import os
import hashlib
from models import BibleVerse, Promise
from flask import send_file
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class DatabaseExporter:
    def __init__(self):
        self.cache_dir = "instance/offline_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def check_space(self, required_mb=50):
        """Verifica espacio disponible"""
        if hasattr(os, 'statvfs'):
            st = os.statvfs(self.cache_dir)
            free_mb = (st.f_bavail * st.f_frsize) / (1024 * 1024)
            return free_mb >= required_mb
        return True  # En sistemas sin statvfs
        
    def calculate_checksum(self, file_path):
        """Calcula checksum del archivo"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()
        
    def verify_database(self, db_path):
        """Verifica integridad de la base de datos"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar estructura
            cursor.execute("SELECT COUNT(*) FROM verses")
            verses_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM promises")
            promises_count = cursor.fetchone()[0]
            
            conn.close()
            
            return verses_count > 0 and promises_count > 0
            
        except Exception as e:
            logger.error(f"Error verificando base de datos: {str(e)}")
            return False
            
    def export_bible_data(self):
        """Exporta los datos bíblicos con validación"""
        try:
            if not self.check_space():
                raise Exception("Espacio insuficiente para la exportación")
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            db_path = f"{self.cache_dir}/offline_bible_{timestamp}.db"
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Crear tablas con índices para mejor rendimiento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verses (
                    id TEXT PRIMARY KEY,
                    book TEXT,
                    chapter INTEGER,
                    verse INTEGER,
                    spanish_text TEXT,
                    tzotzil_text TEXT
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_book_chapter ON verses(book, chapter)")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS promises (
                    id INTEGER PRIMARY KEY,
                    verse_text TEXT,
                    book_reference TEXT,
                    background_image TEXT
                )
            """)
            
            # Exportar datos
            verses = BibleVerse.query.all()
            promises = Promise.query.all()
            
            cursor.executemany(
                "INSERT OR REPLACE INTO verses VALUES (?, ?, ?, ?, ?, ?)",
                [(f"{v.book}-{v.chapter}-{v.verse}", v.book, v.chapter, 
                  v.verse, v.spanish_text, v.tzotzil_text) for v in verses]
            )
            
            cursor.executemany(
                "INSERT OR REPLACE INTO promises VALUES (?, ?, ?, ?)",
                [(p.id, p.verse_text, p.book_reference, p.background_image) 
                 for p in promises]
            )
            
            conn.commit()
            conn.close()
            
            # Verificar integridad
            if not self.verify_database(db_path):
                os.remove(db_path)
                raise Exception("Verificación de integridad fallida")
                
            # Generar y guardar checksum
            checksum = self.calculate_checksum(db_path)
            with open(f"{db_path}.checksum", 'w') as f:
                f.write(checksum)
                
            return db_path
            
        except Exception as e:
            logger.error(f"Error exportando base de datos: {str(e)}")
            raise

def export_bible_data():
    """Función wrapper para mantener compatibilidad"""
    exporter = DatabaseExporter()
    return exporter.export_bible_data()
