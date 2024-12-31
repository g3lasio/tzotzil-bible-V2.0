from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    """Modelo de usuario para autenticación"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    preferences = db.Column(db.JSON, default=dict)
    interaction_count = db.Column(db.Integer, default=0)
    common_themes = db.Column(db.JSON, default=list)
    language_preference = db.Column(db.String(10), default='es')
    
    conversations = db.relationship('Conversation', backref='user', lazy=True)

    def set_password(self, password):
        """Establece la contraseña del usuario"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña del usuario"""
        return check_password_hash(self.password_hash, password)

class BibleVerse(db.Model):
    """Modelo para versículos bíblicos"""
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

class Promise(db.Model):
    """Modelo para promesas bíblicas"""
    __tablename__ = 'promise'

    id = db.Column(db.Integer, primary_key=True)
    verse_text = db.Column(db.Text, nullable=False)
    background_image = db.Column(db.String(255), nullable=False)
    book_reference = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)