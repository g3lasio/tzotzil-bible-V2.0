
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
            # Crear usuario admin de prueba
            test_users = [
                {
                    'username': 'admin',
                    'email': 'admin@test.com',
                    'password': 'Admin123!'
                },
                {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'Test123!'
                }
            ]

            for user_data in test_users:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        is_active=True
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    
            db.session.commit()
            logger.info("Test users created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating test data: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    create_test_data()
