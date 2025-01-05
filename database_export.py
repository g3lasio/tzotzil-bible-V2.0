
import sqlite3
import json
import logging
from models import BibleVerse, Promise
from flask import send_file
from datetime import datetime
import os

logger = logging.getLogger(__name__)

def export_bible_data():
    """Exporta los datos bíblicos a SQLite local"""
    try:
        db_path = "instance/offline_bible.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tablas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verses (
                id TEXT PRIMARY KEY,
                book TEXT,
                chapter INTEGER,
                verse INTEGER,
                spanish_text TEXT,
                tzotzil_text TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promises (
                id INTEGER PRIMARY KEY,
                verse_text TEXT,
                book_reference TEXT,
                background_image TEXT
            )
        """)
        
        # Exportar versículos
        verses = BibleVerse.query.all()
        for verse in verses:
            cursor.execute("""
                INSERT OR REPLACE INTO verses 
                (id, book, chapter, verse, spanish_text, tzotzil_text)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"{verse.book}-{verse.chapter}-{verse.verse}",
                verse.book,
                verse.chapter,
                verse.verse,
                verse.spanish_text,
                verse.tzotzil_text
            ))
            
        # Exportar promesas
        promises = Promise.query.all()
        for promise in promises:
            cursor.execute("""
                INSERT OR REPLACE INTO promises
                (verse_text, book_reference, background_image)
                VALUES (?, ?, ?)
            """, (
                promise.verse_text,
                promise.book_reference,
                promise.background_image
            ))
            
        conn.commit()
        conn.close()
        return db_path
        
    except Exception as e:
        logger.error(f"Error exportando base de datos: {str(e)}")
        raise
