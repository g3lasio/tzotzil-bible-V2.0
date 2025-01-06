
import pytest
from app import create_app
from database import db
from models import User, BibleVerse, Promise
import json

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

@pytest.fixture
def auth_headers(client):
    # Create test user
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!',
        'lastname': 'Test',
        'phone': '1234567890'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    token = json.loads(response.data)['token']
    return {'Authorization': f'Bearer {token}'}

def test_auth_flow(client):
    # Test registro
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!',
        'lastname': 'Test',
        'phone': '1234567890'
    })
    assert response.status_code in [200, 201]

    # Test login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    assert response.status_code == 200
    assert 'token' in json.loads(response.data)

def test_bible_routes(client, auth_headers):
    # Test obtener libros
    response = client.get('/api/bible/books', headers=auth_headers)
    assert response.status_code == 200
    
    # Test obtener capítulos
    response = client.get('/api/bible/chapters/Genesis', headers=auth_headers)
    assert response.status_code == 200

    # Test obtener versículos
    response = client.get('/api/bible/verses/Genesis/1', headers=auth_headers)
    assert response.status_code == 200

def test_nevin_chat(client, auth_headers):
    response = client.post('/api/nevin/chat', 
                         json={'message': 'Test message'},
                         headers=auth_headers)
    assert response.status_code in [200, 401]

def test_user_settings(client, auth_headers):
    response = client.get('/api/user/settings', headers=auth_headers)
    assert response.status_code == 200

    response = client.post('/api/user/settings', 
                          json={'theme': 'dark'},
                          headers=auth_headers)
    assert response.status_code == 200
