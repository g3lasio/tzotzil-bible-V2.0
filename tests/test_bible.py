
import pytest
from bible_data import get_verse, get_chapter, get_book

def test_bible_verse_retrieval(app):
    with app.app_context():
        verse = get_verse("Génesis", 1, 1)
        assert verse is not None
        assert verse['book'] == "Génesis"
        assert verse['chapter'] == 1
        assert verse['verse'] == 1
        assert 'tzotzil_text' in verse
        assert 'spanish_text' in verse

def test_chapter_retrieval(app):
    with app.app_context():
        chapter = get_chapter("Génesis", 1)
        assert chapter is not None
        assert len(chapter) > 0
        assert all('verse' in v for v in chapter)

def test_book_retrieval(app):
    with app.app_context():
        book = get_book("Génesis")
        assert book is not None
        assert 'name' in book
        assert 'chapters' in book
        assert book['name'] == "Génesis"
