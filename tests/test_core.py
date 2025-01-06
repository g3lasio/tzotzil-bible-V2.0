
import pytest
from flask import url_for
from models import User, NevinAccess, BibleVerse, Promise
from database import db
from datetime import datetime, timedelta
import json

@pytest.fixture
def app():
    from app import create_app
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_app_creation(app):
    assert app is not None
    assert app.config['TESTING'] is True

def test_user_model():
    user = User(
        username="testuser",
        email="test@example.com",
        lastname="Test",
        phone="1234567890"
    )
    user.set_password("password123")
    assert user.check_password("password123")
    assert not user.check_password("wrong")
    assert user.lastname == "Test"
    assert user.phone == "1234567890"

def test_nevin_access():
    now = datetime.utcnow()
    access = NevinAccess(
        user_id=1,
        access_type="trial",
        expires_at=now + timedelta(days=7)
    )
    assert access.is_valid()
    
    expired_access = NevinAccess(
        user_id=1,
        access_type="trial",
        expires_at=now - timedelta(days=1)
    )
    assert not expired_access.is_valid()

def test_bible_verse_model():
    verse = BibleVerse(
        book="Génesis",
        chapter=1,
        verse=1,
        tzotzil_text="Ta sba banamil",
        spanish_text="En el principio"
    )
    assert verse.book == "Génesis"
    assert verse.chapter == 1
    assert verse.verse == 1
    assert verse.tzotzil_text == "Ta sba banamil"
    assert verse.spanish_text == "En el principio"

def test_promise_model():
    promise = Promise(
        verse_text="Test promise",
        book_reference="Genesis 1:1",
        background_image="test.jpg"
    )
    assert promise.verse_text == "Test promise"
    assert promise.book_reference == "Genesis 1:1"
    assert promise.background_image == "test.jpg"

def test_user_registration(client):
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Password123!',
        'lastname': 'New',
        'phone': '1234567890'
    })
    assert response.status_code in [200, 201]

def test_user_login(client):
    # Registrar usuario
    client.post('/api/auth/register', json={
        'username': 'logintest',
        'email': 'login@example.com',
        'password': 'Password123!',
        'lastname': 'Test',
        'phone': '1234567890'
    })
    
    # Intentar login
    response = client.post('/api/auth/login', json={
        'email': 'login@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == 200
    assert 'token' in json.loads(response.data)
