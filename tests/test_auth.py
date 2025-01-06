
import pytest
from models import User, NevinAccess
from datetime import datetime, timedelta

def test_user_authentication(app, client):
    with app.app_context():
        # Test registro
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!',
            'lastname': 'Test'
        })
        assert response.status_code in [200, 201]

        # Test login
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test123!'
        })
        assert response.status_code == 200
        assert 'token' in response.get_json()

def test_password_reset(app, client):
    with app.app_context():
        # Test solicitud de reset
        response = client.post('/api/auth/forgot-password', json={
            'email': 'test@example.com'
        })
        assert response.status_code == 200

def test_nevin_access(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('Test123!')
        
        access = NevinAccess(
            user_id=1,
            access_type='trial',
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        assert access.is_valid() == True

        expired_access = NevinAccess(
            user_id=1,
            access_type='trial',
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        assert expired_access.is_valid() == False
