import re
import logging
import sqlite3
from datetime import datetime
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)


class DataValidator:

    @staticmethod
    def validate_bible_verse(book, chapter, verse, tzotzil_text, spanish_text):
        """Validate Bible verse data with enhanced checks"""
        errors = []

        # Validate book name
        if not book or not isinstance(book, str) or not book.strip():
            errors.append(
                "Book name is required and must be a non-empty string")
        elif not all(c.isprintable() for c in book):
            errors.append("Book name contains invalid characters")

        # Validate chapter and verse numbers
        try:
            chapter = int(chapter)
            verse = int(verse)
            if chapter <= 0:
                errors.append("Chapter number must be a positive integer")
            elif chapter > 150:
                errors.append("Chapter number exceeds maximum allowed value")

            if verse <= 0:
                errors.append("Verse number must be a positive integer")
            elif verse > 176:
                errors.append("Verse number exceeds maximum allowed value")
        except (ValueError, TypeError):
            errors.append("Invalid chapter or verse number format")

        # Validate Tzotzil text
        if not tzotzil_text or not isinstance(tzotzil_text,
                                              str) or not tzotzil_text.strip():
            errors.append(
                "Tzotzil text is required and must be a non-empty string")
        else:
            try:
                tzotzil_text.encode('utf-8').decode('utf-8')
                if len(tzotzil_text) > 2000:
                    errors.append("Tzotzil text exceeds maximum length")
                if not any(c.isalpha() for c in tzotzil_text):
                    errors.append(
                        "Tzotzil text must contain at least one letter")
            except UnicodeError:
                errors.append("Tzotzil text contains invalid characters")

        # Validate Spanish text
        if not spanish_text or not isinstance(spanish_text, str):
            errors.append("Spanish text is required and must be a string")
        elif not spanish_text.strip():
            errors.append("Spanish text cannot be empty")
        elif spanish_text.strip(
        ) == "Versículo no traducido debido a manuscritos originales.":
            pass  # Accept special case for untranslated verses
        else:
            try:
                spanish_text.encode('utf-8').decode('utf-8')
                if len(spanish_text) > 2000:
                    errors.append("Spanish text exceeds maximum length")
                if not any(c.isalpha() for c in spanish_text):
                    errors.append(
                        "Spanish text must contain at least one letter")
            except UnicodeError:
                errors.append("Spanish text contains invalid characters")

        return errors

    @staticmethod
    def validate_user_data(email=None, username=None, password=None):
        """Validate user registration/update data"""
        errors = []

        # Email validation
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Invalid email format")
            elif len(email) > 120:
                errors.append("Email is too long (maximum 120 characters)")

        # Username validation
        if username:
            if len(username) < 3:
                errors.append("Username must be at least 3 characters long")
            elif len(username) > 30:
                errors.append("Username cannot exceed 30 characters")
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                errors.append(
                    "Username can only contain letters, numbers, underscores, and hyphens"
                )

        # Password validation
        if password:
            if len(password) < 8:
                errors.append("Password must be at least 8 characters long")
            elif len(password) > 128:
                errors.append("Password cannot exceed 128 characters")
            if not re.search(r'[A-Z]', password):
                errors.append(
                    "Password must contain at least one uppercase letter")
            if not re.search(r'[a-z]', password):
                errors.append(
                    "Password must contain at least one lowercase letter")
            if not re.search(r'\d', password):
                errors.append("Password must contain at least one number")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors.append(
                    "Password must contain at least one special character")

        return errors

    @staticmethod
    def validate_favorite(user_id, verse_id):
        """Validate favorite data"""
        errors = []

        try:
            user_id = int(user_id)
            verse_id = int(verse_id)
            if user_id <= 0:
                errors.append("Invalid user ID")
            if verse_id <= 0:
                errors.append("Invalid verse ID")
        except (ValueError, TypeError):
            errors.append("User ID and verse ID must be valid integers")

        return errors

    @staticmethod
    def validate_database_connection(db):
        """Validate database connection and basic queries"""
        try:
            if db is None:
                return False, "Database connection is None"

            # Test database connection
            cursor = db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("SELECT 1")
            
            return True, None
        except sqlite3.OperationalError as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Database validation failed: {str(e)}"

    @staticmethod
    def validate_request(required_fields=None, allowed_fields=None):
        """Decorator for validating request data"""

        def decorator(f):

            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json(
                ) if request.is_json else request.form.to_dict()
                errors = []

                # Check required fields
                if required_fields:
                    missing_fields = [
                        field for field in required_fields if field not in data
                    ]
                    if missing_fields:
                        errors.append(
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )

                # Check for unknown fields
                if allowed_fields:
                    unknown_fields = [
                        field for field in data if field not in allowed_fields
                    ]
                    if unknown_fields:
                        errors.append(
                            f"Unknown fields: {', '.join(unknown_fields)}")

                if errors:
                    return jsonify({
                        'status': 'error',
                        'message': 'Validation failed',
                        'errors': errors
                    }), 400

                return f(*args, **kwargs)

            return decorated_function

        return decorator
