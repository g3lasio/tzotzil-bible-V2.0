import csv
import os
from flask import Flask
from extensions import db, init_extensions
from models import Promise
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_promises():
    try:
        # Initialize Flask app
        app = Flask(__name__)
        
        # Configure database
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize extensions
        init_extensions(app)
        
        with app.app_context():
            # Verify if promises.csv exists
            if not os.path.exists('promesas.csv'):
                logger.error("El archivo promesas.csv no existe")
                return
            
            logger.info("Iniciando importación de promesas...")
            
            # Read CSV file
            with open('promesas.csv', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Clean column names
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                logger.info(f"Columnas encontradas: {reader.fieldnames}")
                
                promises_count = 0
                for row in reader:
                    try:
                        # Create new promise
                        new_promise = Promise(
                            verse_text=row['text'].strip(),
                            background_image=row['imageUrl'].strip(),
                            book_reference=row['text'].split(' - ')[0].strip()
                        )
                        db.session.add(new_promise)
                        promises_count += 1
                        
                        # Commit every 100 records
                        if promises_count % 100 == 0:
                            db.session.commit()
                            logger.info(f"Importadas {promises_count} promesas...")
                            
                    except KeyError as e:
                        logger.error(f"Error: Columna no encontrada: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error al procesar fila: {e}")
                        continue
                
                # Final commit for remaining records
                db.session.commit()
                logger.info(f"Importación completada. Total de promesas importadas: {promises_count}")
                
    except Exception as e:
        logger.error(f"Error durante la importación: {e}")
        if hasattr(db, 'session'):
            db.session.rollback()
        raise

if __name__ == '__main__':
    import_promises()
