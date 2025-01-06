
import pytest
from bible_data_access import BibleDataAccess
from models import BibleVerse
from database import db

@pytest.fixture
def bible_data():
    return BibleDataAccess()

def test_get_verse(app, bible_data):
    with app.app_context():
        # Crear versículo de prueba
        verse = BibleVerse(
            book="Génesis",
            chapter=1,
            verse=1,
            tzotzil_text="Ta sba banamil",
            spanish_text="En el principio"
        )
        db.session.add(verse)
        db.session.commit()
        
        result = bible_data.get_verse("Génesis", 1, 1)
        assert result['success'] is True
        assert result['data']['spanish_text'] == "En el principio"
        assert result['data']['tzotzil_text'] == "Ta sba banamil"

def test_get_chapter(app, bible_data):
    with app.app_context():
        # Crear múltiples versículos
        verses = [
            BibleVerse(book="Génesis", chapter=1, verse=i, 
                      tzotzil_text=f"Verso {i}", 
                      spanish_text=f"Versículo {i}")
            for i in range(1, 4)
        ]
        db.session.bulk_save_objects(verses)
        db.session.commit()
        
        result = bible_data.get_chapter("Génesis", 1)
        assert result['success'] is True
        assert len(result['data']) == 3

def test_verse_not_found(app, bible_data):
    with app.app_context():
        result = bible_data.get_verse("Libro Inexistente", 1, 1)
        assert result['success'] is False
        assert "no encontrado" in result['error'].lower()

def test_cache_functionality(app, bible_data):
    with app.app_context():
        # Primera llamada - sin caché
        bible_data.get_verse("Génesis", 1, 1)
        # Segunda llamada - debería usar caché
        result = bible_data.get_verse("Génesis", 1, 1)
        assert result is not None

def test_invalid_input(app, bible_data):
    with app.app_context():
        result = bible_data.get_verse("", -1, 0)
        assert result['success'] is False
