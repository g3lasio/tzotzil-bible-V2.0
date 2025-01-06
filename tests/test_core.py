
import pytest
from flask import url_for
from models import User, NevinAccess
from validation import DataValidator
from database import db
from datetime import datetime, timedelta

def test_bible_verse_validation():
    validator = DataValidator()
    
    # Caso válido
    errors = validator.validate_bible_verse(
        book="Génesis",
        chapter=1,
        verse=1,
        tzotzil_text="Ta sba banamil ti Riox spasoje",
        spanish_text="En el principio creó Dios los cielos y la tierra"
    )
    assert len(errors) == 0

    # Casos inválidos
    errors = validator.validate_bible_verse(
        book="",
        chapter=-1,
        verse=0,
        tzotzil_text="",
        spanish_text=""
    )
    assert len(errors) > 0

def test_user_authentication():
    # Test registro
    test_user = User(
        username="test_user",
        email="test@example.com"
    )
    test_user.set_password("Test123!")
    assert test_user.check_password("Test123!")
    assert not test_user.check_password("WrongPass123!")

def test_nevin_access():
    test_access = NevinAccess(
        user_id=1,
        access_type="trial",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    assert test_access.is_valid()
    
    expired_access = NevinAccess(
        user_id=2,
        access_type="trial",
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    assert not expired_access.is_valid()

@pytest.mark.parametrize("email,expected", [
    ("valid@email.com", True),
    ("invalid.email", False),
    ("", False),
    ("test@test@test.com", False)
])
def test_email_validation(email, expected):
    validator = DataValidator()
    errors = validator.validate_user_data(email=email)
    is_valid = len(errors) == 0
    assert is_valid == expected
