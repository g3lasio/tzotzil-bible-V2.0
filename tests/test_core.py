
import pytest
from flask import url_for
from models import User, NevinAccess, BibleVerse, Promise
from database import db
from datetime import datetime, timedelta
import json

@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_app_creation(app):
    assert app is not None
    assert app.config['TESTING'] is True

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

def test_user_model():
    user = User(
        username="testuser",
        email="test@example.com",
        lastname="Test"
    )
    user.set_password("password123")
    assert user.check_password("password123")
    assert not user.check_password("wrong")

def test_nevin_access():
    access = NevinAccess(
        user_id=1,
        access_type="trial",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    assert access.is_valid()

def test_promise_model():
    promise = Promise(
        verse_text="Test promise",
        book_reference="Genesis 1:1"
    )
    assert promise.verse_text == "Test promise"
    assert promise.book_reference == "Genesis 1:1"
