from flask import Flask
from models import User, BibleVerse
from extensions import db
import logging
from app import create_app

logger = logging.getLogger(__name__)

def create_test_data():
    """Create test data for validation checks"""
    app = create_app()

    with app.app_context():
        try:
            # Verificar si el usuario de prueba ya existe
            existing_user = User.query.filter_by(username="testuser").first()
            if existing_user:
                logger.info("Test user already exists")
                return True

            # Create test user
            test_user = User(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="User"
            )
            test_user.set_password("Test@123456")
            db.session.add(test_user)
            db.session.commit()
            logger.info("Test user created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating test data: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    create_test_data()