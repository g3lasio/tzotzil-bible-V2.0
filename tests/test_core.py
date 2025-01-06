
import pytest
from flask import url_for
from models import User, NevinAccess, BibleVerse, Promise
from validation import DataValidator
from database import db
from datetime import datetime, timedelta
import json

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
        lastname="Test",
        phone="1234567890"
    )
    user.set_password("TestPass123!")
    assert user.check_password("TestPass123!")
    assert not user.check_password("WrongPass")

def test_promise_model():
    promise = Promise(
        verse_text="Test promise",
        book_reference="Genesis 1:1",
        background_image="test.jpg"
    )
    assert promise.verse_text == "Test promise"
    assert promise.book_reference == "Genesis 1:1"

def test_validation():
    validator = DataValidator()
    
    # Test Bible verse validation
    errors = validator.validate_bible_verse(
        "Génesis", 1, 1,
        "Test tzotzil", "Test spanish"
    )
    assert len(errors) == 0

    # Test invalid data
    errors = validator.validate_bible_verse(
        "", -1, 0, "", ""
    )
    assert len(errors) > 0

def test_user_validation():
    validator = DataValidator()
    
    # Test valid data
    errors = validator.validate_user_data(
        email="test@example.com",
        username="testuser",
        password="TestPass123!"
    )
    assert len(errors) == 0

    # Test invalid data
    errors = validator.validate_user_data(
        email="invalid-email",
        username="a",
        password="weak"
    )
    assert len(errors) > 0
