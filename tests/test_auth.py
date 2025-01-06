
import pytest
from flask import url_for
from models import User
from database import db

def test_register(client):
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!',
        'lastname': 'Test'
    })
    assert response.status_code in [200, 201]

def test_login(client):
    # Crear usuario de prueba
    user = User(username='testuser', email='test@example.com', lastname='Test')
    user.set_password('Test123!')
    db.session.add(user)
    db.session.commit()

    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_reset_password(client):
    response = client.post('/api/auth/forgot-password', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 200
