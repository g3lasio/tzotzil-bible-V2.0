
import pytest
from flask import url_for
from models import User, NevinAccess, BibleVerse, Promise
from validation import DataValidator
from database import db
from datetime import datetime, timedelta
import json

class TestUserModel:
    def test_user_creation(self):
        user = User(
            username="testuser",
            email="test@example.com",
            lastname="Test",
            phone="1234567890"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.lastname == "Test"

    def test_password_hashing(self):
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        assert user.password_hash is not None
        assert user.check_password("password123")
        assert not user.check_password("wrongpassword")

class TestBibleVerse:
    def test_bible_verse_creation(self):
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

class TestValidation:
    def test_bible_verse_validation(self):
        validator = DataValidator()
        errors = validator.validate_bible_verse(
            book="Génesis", 
            chapter=1, 
            verse=1,
            tzotzil_text="Test tzotzil", 
            spanish_text="Test spanish"
        )
        assert len(errors) == 0

        # Prueba datos inválidos
        errors = validator.validate_bible_verse(
            book="", 
            chapter=-1, 
            verse=0,
            tzotzil_text="", 
            spanish_text=""
        )
        assert len(errors) > 0

    def test_user_validation(self):
        validator = DataValidator()
        errors = validator.validate_user_data(
            email="test@example.com",
            username="validuser",
            password="ValidPass123!"
        )
        assert len(errors) == 0

        errors = validator.validate_user_data(
            email="invalid-email",
            username="a",
            password="weak"
        )
        assert len(errors) > 0

class TestNevinAccess:
    def test_nevin_access_validation(self):
        access = NevinAccess(
            user_id=1,
            access_type="trial",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        assert access.is_valid() == True

        expired_access = NevinAccess(
            user_id=1,
            access_type="trial",
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        assert expired_access.is_valid() == False

class TestPromise:
    def test_promise_creation(self):
        promise = Promise(
            verse_text="Test promise",
            book_reference="Genesis 1:1",
            background_image="test.jpg"
        )
        assert promise.verse_text == "Test promise"
        assert promise.book_reference == "Genesis 1:1"
        assert promise.background_image == "test.jpg"
