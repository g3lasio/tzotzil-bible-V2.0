
from extensions import db

class BibleVerse(db.Model):
    """Modelo para versículos bíblicos"""
    __tablename__ = 'bibleverse'

    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(50), nullable=False, index=True)
    chapter = db.Column(db.Integer, nullable=False, index=True)
    verse = db.Column(db.Integer, nullable=False, index=True)
    tzotzil_text = db.Column(db.Text, nullable=False)
    spanish_text = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.Index('idx_book_chapter_verse', 'book', 'chapter', 'verse'),
        db.Index('idx_book_order', 'book', 'order_index'),
    )
