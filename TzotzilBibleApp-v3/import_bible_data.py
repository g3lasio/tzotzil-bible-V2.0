
import csv
import logging
from flask import Flask
from models import BibleVerse, db
from extensions import init_extensions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_bible_data(csv_file='Tzotzil_database.csv'):
    try:
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/bible_app.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        init_extensions(app)
        
        with app.app_context():
            # Crear tablas
            db.create_all()
            
            # Verificar si ya existen datos
            verse_count = db.session.query(BibleVerse).count()
            if verse_count > 0:
                logger.info(f"Limpiando {verse_count} versículos existentes...")
                db.session.query(BibleVerse).delete()
                db.session.commit()
            
            logger.info(f"Importando desde {csv_file}...")
            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                verses = []
                for row in reader:
                    verse = BibleVerse(
                        book=row['Libro'],
                        chapter=int(row['Capítulo']),
                        verse=int(row['Versículo']),
                        tzotzil_text=row['Texto Tzotzil'],
                        spanish_text=row['Texto Español']
                    )
                    verses.append(verse)
                    
                    if len(verses) >= 500:
                        db.session.bulk_save_objects(verses)
                        db.session.commit()
                        logger.info(f"Importados {len(verses)} versículos...")
                        verses = []
                
                if verses:
                    db.session.bulk_save_objects(verses)
                    db.session.commit()
                    logger.info(f"Importados {len(verses)} versículos finales")
            
            # Verificar importación
            final_count = db.session.query(BibleVerse).count()
            logger.info(f"Importación completada. Total versículos: {final_count}")
            return True
            
    except Exception as e:
        logger.error(f"Error en importación: {str(e)}")
        return False

if __name__ == "__main__":
    import_bible_data()
