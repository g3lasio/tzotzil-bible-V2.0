
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expires = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

class Promise(db.Model):
    __tablename__ = 'promise'
    id = db.Column(db.Integer, primary_key=True)
    verse_text = db.Column(db.Text, nullable=False)
    book_reference = db.Column(db.String(100), nullable=False)
    background_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class BibleVerse(db.Model):
    __tablename__ = 'bibleverse'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(50), nullable=False, index=True)
    chapter = db.Column(db.Integer, nullable=False, index=True)
    verse = db.Column(db.Integer, nullable=False, index=True)
    tzotzil_text = db.Column(db.Text, nullable=False)
    spanish_text = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.Index('idx_book_chapter_verse', 'book', 'chapter', 'verse'),
    )
