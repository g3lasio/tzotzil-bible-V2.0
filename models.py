from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """Modelo simplificado de Usuario con autenticación JWT"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        """Establece la contraseña del usuario"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña del usuario"""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Retorna el ID del usuario como string"""
        return str(self.id)

    def to_dict(self):
        """Convierte el usuario a diccionario para JWT"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active
        }

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

class Promise(db.Model):
    __tablename__ = 'promise'
    id = db.Column(db.Integer, primary_key=True)
    verse_text = db.Column(db.Text, nullable=False)
    book_reference = db.Column(db.String(100), nullable=False)
    background_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())