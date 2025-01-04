from datetime import datetime, timedelta
from flask_login import UserMixin
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """Modelo de usuario mejorado con sistema de suscripciones"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    nevin_access = db.Column(db.Boolean, default=True)
    trial_ends_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=21))
    trial_started_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Nuevos campos para suscripciones
    plan_type = db.Column(db.String(20), default='Free', nullable=False)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(20), default='inactive', nullable=False)

    def has_nevin_access(self):
        """Verifica si el usuario tiene acceso a Nevin basado en su plan y prueba"""
        now = datetime.utcnow()
        
        # Si es usuario premium activo
        if self.plan_type == 'Premium' and self.subscription_status == 'active':
            return True
            
        # Verifica período de prueba
        if self.trial_started_at and self.trial_ends_at:
            in_trial = now <= self.trial_ends_at
            if not in_trial and self.nevin_access:
                self.nevin_access = False
                db.session.commit()
            return in_trial
            
        return False

    def is_premium(self):
        """Verifica si el usuario tiene plan Premium activo"""
        return self.plan_type == 'Premium' and self.subscription_status == 'active'

    def is_in_trial(self):
        """Verifica si el usuario está en período de prueba"""
        if not self.trial_ends_at or not self.trial_started_at:
            return False
        return datetime.utcnow() <= self.trial_ends_at

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

    def upgrade_to_premium(self):
        """Actualiza el usuario a plan premium"""
        self.plan_type = 'Premium'
        self.subscription_status = 'active'
        self.subscription_start = datetime.utcnow()
        self.nevin_access = True
        db.session.commit()
        return True

    def to_dict(self):
        """Convierte el usuario a un diccionario"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'plan_type': self.plan_type,
            'subscription_status': self.subscription_status,
            'is_in_trial': self.is_in_trial(),
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'nevin_access': self.has_nevin_access()
        }

# Mantener las otras clases sin cambios
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