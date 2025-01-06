
import pytest
from bible_data_access import get_verse, get_chapter, get_book
from models import BibleVerse
from database import db

def test_get_verse(app):
    with app.app_context():
        verse = BibleVerse(
            book="Génesis",
            chapter=1,
            verse=1,
            tzotzil_text="Test tzotzil",
            spanish_text="Test spanish"
        )
        db.session.add(verse)
        db.session.commit()
        
        result = get_verse("Génesis", 1, 1)
        assert result is not None
        assert result.spanish_text == "Test spanish"

def test_get_chapter(app):
    with app.app_context():
        verse = BibleVerse(
            book="Génesis",
            chapter=1,
            verse=1,
            tzotzil_text="Test tzotzil",
            spanish_text="Test spanish"
        )
        db.session.add(verse)
        db.session.commit()
        
        result = get_chapter("Génesis", 1)
        assert len(result) > 0

def test_get_book(app):
    with app.app_context():
        verse = BibleVerse(
            book="Génesis",
            chapter=1,
            verse=1,
            tzotzil_text="Test tzotzil",
            spanish_text="Test spanish"
        )
        db.session.add(verse)
        db.session.commit()
        
        result = get_book("Génesis")
        assert result is not None
        assert result['name'] == "Génesis"
