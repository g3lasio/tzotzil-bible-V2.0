import logging
from app import create_app
from extensions import db
from flask_migrate import Migrate, upgrade
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa la base de datos y aplica las migraciones"""
    try:
        app = create_app()
        if not app:
            logger.error("No se pudo crear la aplicación Flask")
            return False

        migrate = Migrate(app, db)

        with app.app_context():
            # Verificar conexión a la base de datos
            try:
                db.session.execute(text('SELECT 1'))
                logger.info("Conexión a base de datos verificada")
            except Exception as e:
                logger.error(f"Error conectando a la base de datos: {str(e)}")
                return False

            # Crear todas las tablas
            try:
                db.create_all()
                logger.info("Tablas creadas correctamente")
            except Exception as e:
                logger.error(f"Error creando tablas: {str(e)}")
                return False

            # Aplicar migraciones
            try:
                upgrade()
                logger.info("Migraciones aplicadas correctamente")
            except Exception as e:
                logger.error(f"Error aplicando migraciones: {str(e)}")
                return False

            return True

    except Exception as e:
        logger.error(f"Error en la inicialización de la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("Base de datos inicializada correctamente")
    else:
        print("Error inicializando la base de datos")
        exit(1)