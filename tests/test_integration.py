
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

def test_home_route(client):
    response = client.get('/')
    assert response.status_code in [200, 302]

def test_bible_routes(client):
    # Test books list
    response = client.get('/books')
    assert response.status_code == 200

    # Test specific book
    response = client.get('/chapter/Génesis/1')
    assert response.status_code == 200

def test_search_functionality(client):
    response = client.get('/search?keyword=amor&version=spanish')
    assert response.status_code == 200

def test_user_auth_flow(client):
    # Test registration
    signup_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'lastname': 'Test',
        'phone': '1234567890'
    }
    response = client.post('/api/auth/register', json=signup_data)
    assert response.status_code in [201, 200]

    # Test login
    login_data = {
        'email': 'test@example.com',
        'password': 'TestPass123!'
    }
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 200

def test_nevin_chat(client):
    response = client.post('/api/nevin/chat', 
                         json={'message': 'Test message'})
    assert response.status_code in [200, 401]

def test_settings_routes(client):
    response = client.get('/settings')
    assert response.status_code in [200, 302]
