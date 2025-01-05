from datetime import datetime, timedelta
from flask_login import UserMixin
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """Modelo de usuario mejorado con sistema de suscripciones"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    __table_args__ = {'postgresql_using': 'btree'}
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    lastname = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    nevin_access = db.Column(db.Boolean, default=True)


    def has_nevin_access(self):
        """Verifica si el usuario tiene acceso a Nevin"""
        return self.nevin_access

    def set_password(self, password):
        """Establece la contraseña del usuario"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña del usuario"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Obtiene el ID del usuario"""
        return str(self.id)

    def to_dict(self):
        """Convierte el usuario a un diccionario"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'nevin_access': self.has_nevin_access()
        }

class BibleVerse(db.Model):
    __tablename__ = 'bibleverse'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(50), nullable=False, index=True)
    chapter = db.Column(db.Integer, nullable=False, index=True)
    verse = db.Column(db.Integer, nullable=False, index=True)
    tzotzil_text = db.Column(db.Text, nullable=False)
    spanish_text = db.Column(db.Text, nullable=False)

class Promise(db.Model):
    __tablename__ = 'promise'
    id = db.Column(db.Integer, primary_key=True)
    verse_text = db.Column(db.Text, nullable=False)
    book_reference = db.Column(db.String(100), nullable=False)
    background_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())