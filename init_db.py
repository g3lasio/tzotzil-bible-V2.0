from app import create_app
from extensions import db
from flask_migrate import Migrate, upgrade

app = create_app()
migrate = Migrate(app, db)

def init_database():
    with app.app_context():
        # Crear todas las tablas
        db.create_all()

        # Aplicar migraciones
        upgrade()

if __name__ == "__main__":
    init_database()
    print("Base de datos inicializada correctamente")