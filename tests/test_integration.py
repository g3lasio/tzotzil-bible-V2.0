
import pytest
from app import create_app
from database import db
from models import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_bible_route(client):
    response = client.get('/api/bible/verses/Génesis/1/1')
    assert response.status_code == 200
    data = response.get_json()
    assert 'tzotzil' in data
    assert 'spanish' in data

def test_user_registration(client):
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    assert response.status_code == 201

def test_nevin_chat(client):
    # Crear usuario de prueba
    user = User(username='testuser', email='test@example.com')
    user.set_password('Test123!')
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()
        
    # Login
    client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    
    # Probar chat
    response = client.post('/api/nevin/chat', json={
        'message': '¿Qué dice Génesis 1:1?'
    })
    assert response.status_code == 200
