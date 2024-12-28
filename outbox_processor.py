import sqlite3
import logging
from datetime import datetime
from validation import DataValidator

# Configure logging
logger = logging.getLogger(__name__)
validator = DataValidator()

def get_db():
    return sqlite3.connect('bible_app.db')

def add_favorite(user_id, verse_id):
    # Validate inputs
    errors = validator.validate_favorite(user_id, verse_id)
    if errors:
        error_msg = ', '.join(errors)
        logger.error(f"Validation failed: {error_msg}")
        raise ValueError(error_msg)

    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Verify user exists
        cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            raise ValueError("User not found")
            
        # Verify verse exists
        cur.execute("SELECT id FROM bibleverse WHERE id = ?", (verse_id,))
        if not cur.fetchone():
            raise ValueError("Verse not found")
        
        # Check for duplicate
        cur.execute("""
            SELECT id FROM favorite 
            WHERE user_id = ? AND verse_id = ?
        """, (user_id, verse_id))
        if cur.fetchone():
            raise ValueError("Favorite already exists")
        
        cur.execute('''
            INSERT INTO favorite (user_id, verse_id, created_at)
            VALUES (?, ?, ?)
        ''', (user_id, verse_id, datetime.utcnow()))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding favorite: {str(e)}")
        raise
    finally:
        conn.close()

def remove_favorite(user_id, verse_id):
    # Validate inputs
    errors = validator.validate_favorite(user_id, verse_id)
    if errors:
        error_msg = ', '.join(errors)
        logger.error(f"Validation failed: {error_msg}")
        raise ValueError(error_msg)

    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Verify favorite exists
        cur.execute("""
            SELECT id FROM favorite 
            WHERE user_id = ? AND verse_id = ?
        """, (user_id, verse_id))
        if not cur.fetchone():
            raise ValueError("Favorite not found")
        
        cur.execute('''
            DELETE FROM favorite
            WHERE user_id = ? AND verse_id = ?
        ''', (user_id, verse_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error removing favorite: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Outbox processor updated with data validation")
