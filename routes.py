from flask import Blueprint, request, Flask, jsonify, render_template, redirect, url_for, g, session, flash
from flask_login import login_required, current_user
from database import db_manager, get_db
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import text
from auth import auth
from models import Promise, BibleVerse
from flask import current_app
from database import get_sorted_books
import logging
import csv
import random
import os
import sqlite3
import time
from validation import DataValidator

logger = logging.getLogger(__name__)
routes = Blueprint('routes', __name__)

logger = logging.getLogger(__name__)
routes = Blueprint('routes', __name__)
validator = DataValidator()

# Biblical order of books
BIBLE_BOOKS_ORDER = [
    # Old Testament
    'Génesis',
    'Éxodo',
    'Levítico',
    'Números',
    'Deuteronomio',
    'Josué',
    'Jueces',
    'Rut',
    '1 Samuel',
    '2 Samuel',
    '1 Reyes',
    '2 Reyes',
    '1 Crónicas',
    '2 Crónicas',
    'Esdras',
    'Nehemías',
    'Ester',
    'Job',
    'Salmos',
    'Proverbios',
    'Eclesiastés',
    'Cantares',
    'Isaías',
    'Jeremías',
    'Lamentaciones',
    'Ezequiel',
    'Daniel',
    'Oseas',
    'Joel',
    'Amós',
    'Abdías',
    'Jonás',
    'Miqueas',
    'Nahúm',
    'Habacuc',
    'Sofonías',
    'Hageo',
    'Zacarías',
    'Malaquías',
    # New Testament
    'Mateo',
    'Marcos',
    'Lucas',
    'Juan',
    'Hechos',
    'Romanos',
    '1 Corintios',
    '2 Corintios',
    'Gálatas',
    'Efesios',
    'Filipenses',
    'Colosenses',
    '1 Tesalonicenses',
    '2 Tesalonicenses',
    '1 Timoteo',
    '2 Timoteo',
    'Tito',
    'Filemón',
    'Hebreos',
    'Santiago',
    '1 Pedro',
    '2 Pedro',
    '1 Juan',
    '2 Juan',
    '3 Juan',
    'Judas',
    'Apocalipsis'
]


@routes.before_request
def validate_database():
    """Validate database connection before each request"""
    try:
        if request.endpoint and not request.endpoint.startswith('static'):
            health_status = db_manager.check_health()
            if not health_status['is_healthy']:
                logger.error(f"Database validation failed: {health_status['error']}")
                return jsonify({
                    'error': 'Database validation failed',
                    'details': health_status['error']
                }), 500

    except Exception as e:
        logger.error(f"Error in database validation: {str(e)}")
        return jsonify({
            'error': 'Database error occurred',
            'details': str(e)
        }), 500


@routes.route('/validate_test', methods=['GET'])
def validate_test():
    """Test route to verify validation functionality"""
    try:
        logger.info("Starting validation test")

        # Test Bible verse validation
        logger.info("Testing Bible verse validation")
        bible_verse_valid = validator.validate_bible_verse(
            "Génesis", "1", "1", "Test Tzotzil text", "Test Spanish text")
        bible_verse_invalid = validator.validate_bible_verse(
            "", "-1", "0", "", "")

        # Test user data validation
        logger.info("Testing user data validation")
        user_valid = validator.validate_user_data(email="test@example.com",
                                                  username="testuser",
                                                  password="Test@123456")
        user_invalid = validator.validate_user_data(email="invalid-email",
                                                    username="a",
                                                    password="weak")

        # Test database connection
        logger.info("Testing database connection")
        db = get_db()
        db_valid, db_error = validator.validate_database_connection(db)

        # Si la función sigue validando la existencia de la tabla 'favorite', podrías eliminar este fragmento

        results = {
            'bible_verse': {
                'valid_test': len(bible_verse_valid) == 0,
                'valid_errors': bible_verse_valid,
                'invalid_test': len(bible_verse_invalid) > 0,
                'invalid_errors': bible_verse_invalid
            },
            'user_data': {
                'valid_test': len(user_valid) == 0,
                'valid_errors': user_valid,
                'invalid_test': len(user_invalid) > 0,
                'invalid_errors': user_invalid
            },
            'database': {
                'connection_valid': db_valid,
                'connection_error': db_error
            }
        }

        logger.info("Validation tests completed successfully")
        return jsonify({
            'status': 'success',
            'message': 'All validation tests completed',
            'validation_results': results
        })

    except Exception as e:
        logger.error(f"Error during validation test: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation test failed',
            'error': str(e)
        }), 500


@routes.route('/random_promise', methods=['GET'])
def random_promise():
    try:
        # Usar directamente la sesión de SQLAlchemy
        total_promises = Promise.query.count()

        if total_promises == 0:
            logger.warning("No hay promesas disponibles en la base de datos")
            return jsonify({
                'status': 'error',
                'message': 'No hay promesas disponibles'
            }), 404

        random_index = random.randint(0, total_promises - 1)
        random_promise = Promise.query.offset(random_index).first()

        if not random_promise:
            logger.error("No se pudo obtener la promesa aleatoria")
            return jsonify({
                'status': 'error',
                'message': 'Error al obtener la promesa'
            }), 500

        return jsonify({
            'status': 'success',
            'verse_text': random_promise.verse_text,
            'background_image': random_promise.background_image,
            'book_reference': random_promise.book_reference
        })
    except Exception as e:
        logger.error(f"Error al obtener la promesa: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error al obtener la promesa'
        }), 500


@routes.route('/')
def index():
    logger.info("Accessing index route")
    try:
        logger.info("Rendering index.html template")
        # Obtener una promesa aleatoria de la base de datos
        total_promises = Promise.query.count()

        # Si no hay promesas disponibles, mostrar un mensaje adecuado
        if total_promises == 0:
            return render_template('index.html', promise=None)

        # Seleccionar una promesa aleatoria
        random_index = random.randint(0, total_promises - 1)
        random_promise = Promise.query.offset(random_index).first()

        # Pasar la promesa al template
        return render_template('index.html', promise=random_promise)

    except Exception as e:
        logger.error(f"Error al cargar la página de inicio: {str(e)}")
        return render_template(
            'index.html',
            promise=None,
            error_message="Hubo un error al cargar la promesa")


@routes.route('/books')
def books():
    try:
        logger.info("Iniciando ruta /books...")

        # Usar el gestor de base de datos con caché
        books_result = db_manager.get_books()

        if not books_result['success']:
            logger.error(f"Error al obtener libros: {books_result['error']}")
            return render_template('error.html', 
                                error="Error al cargar los libros. Por favor, intente más tarde."), 500

        books = books_result['data']
        if not books:
            logger.warning("No se encontraron libros en la base de datos")
            return render_template('error.html', 
                                error="No hay datos bíblicos disponibles en este momento."), 503

        # Ordenar libros según el orden bíblico usando la función auxiliar
        sorted_books = get_sorted_books()

        logger.info(f"Se encontraron y ordenaron {len(sorted_books)} libros correctamente (tiempo: {books_result.get('query_time', 0):.2f}s)")
        return render_template('books.html', books=sorted_books)

    except Exception as e:
        logger.error(f"Error al cargar los libros: {str(e)}")
        return render_template('error.html', 
                             error="Error al cargar los libros. Por favor, intente más tarde."), 500


@routes.route('/chapter/<book>/<int:chapter>')
@routes.route('/chapter/<book>')
@routes.route('/chapter')
def chapter(book=None, chapter=None):
    try:
        book = book or request.args.get('book')
        chapter_str = request.args.get('chapter') if chapter is None else str(chapter)

        if not book:
            logger.warning("Falta parámetro de libro")
            return redirect(url_for('routes.index'))

        # Si no se proporciona capítulo, obtener la lista de capítulos disponibles
        if chapter_str is None:
            chapters_result = db_manager.get_verses(book)
            if not chapters_result['success']:
                logger.error(f"Error al obtener capítulos: {chapters_result['error']}")
                return render_template('error.html',
                                    error="Error al obtener los capítulos"), 500

            chapters = chapters_result['data'].get('chapters', [])
            if not chapters:
                logger.warning(f"No se encontraron capítulos para el libro {book}")
                return render_template('error.html',
                                    error="No se encontraron capítulos"), 404

            return render_template('chapters.html',
                                book=book,
                                chapters=chapters,
                                books=get_sorted_books())

        # Si se proporciona capítulo, convertirlo a entero
        try:
            chapter = int(chapter_str)
        except ValueError:
            logger.error(f"Número de capítulo inválido: {chapter_str}")
            return render_template('error.html',
                                error="Número de capítulo inválido"), 400

        if book not in BIBLE_BOOKS_ORDER:
            logger.error(f"Nombre de libro inválido: {book}")
            return render_template('error.html',
                                error="Libro no encontrado"), 404

        logger.info(f"Buscando versículos para {book} capítulo {chapter}")

        # Usar el gestor de base de datos con caché para obtener versículos
        verses_result = db_manager.get_verses(book, chapter)

        if not verses_result['success']:
            logger.error(f"Error al obtener versículos: {verses_result['error']}")
            return render_template('error.html',
                                error="Error al acceder a la base de datos"), 500

        verses = verses_result['data'].get('verses', [])
        if not verses and chapter is not None:
            logger.warning(f"No se encontraron versículos para {book} capítulo {chapter}")
            return render_template('error.html',
                                error="No se encontraron versículos"), 404

        # Obtener libros ordenados usando la función con caché
        sorted_books = get_sorted_books()

        # Obtener el número máximo de capítulos
        max_chapter_result = db_manager.get_session().execute(
            text("SELECT MAX(chapter) FROM bibleverse WHERE book = :book"),
            {'book': book}
        ).scalar()

        logger.info(f"Capítulo máximo para {book}: {max_chapter_result}")
        logger.info(f"Tiempo de consulta: {verses_result.get('query_time', 0):.2f}s")

        return render_template(
            'chapter.html',
            book=book,
            chapter=chapter,
            verses=verses,
            max_chapter=max_chapter_result,
            books=sorted_books
        )

    except Exception as e:
        logger.error(f"Error en la ruta chapter: {str(e)}", exc_info=True)
        return render_template('error.html',
                            error="Ha ocurrido un error. Por favor, intente más tarde."), 500


@routes.route('/search')
def search():
    try:
        logger.info("Iniciando búsqueda")
        books = get_sorted_books()
        if not books:
            logger.error("No se encontraron libros en la base de datos")
            return render_template('error.html', error="No hay datos bíblicos disponibles")

        if not request.args.get('keyword'):
            return render_template('search.html',
                                 books=books,
                                 versions=['tzotzil', 'spanish'],
                                 testament='both',
                                 book='all')

        keyword = request.args.get('keyword', '').strip()
        versions = request.args.getlist('version') or ['tzotzil', 'spanish']
        testament = request.args.get('testament', 'both')
        book = request.args.get('book', 'all')

        # Usar SQLAlchemy para la consulta
        from models import BibleVerse
        query = BibleVerse.query

        if book != 'all':
            query = query.filter(BibleVerse.book == book)

        if testament != 'both':
            query = query.filter(BibleVerse.testament == testament)

        # Construir condiciones de búsqueda
        search_conditions = []
        if 'tzotzil' in versions:
            search_conditions.append(BibleVerse.tzotzil_text.ilike(f'%{keyword}%'))
        if 'spanish' in versions:
            search_conditions.append(BibleVerse.spanish_text.ilike(f'%{keyword}%'))

        if search_conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*search_conditions))

        # Ordenar resultados
        results = query.order_by(BibleVerse.book, BibleVerse.chapter, BibleVerse.verse).all()

        # Convertir resultados a diccionarios
        results_dict = [{
            'id': verse.id,
            'book': verse.book,
            'chapter': verse.chapter,
            'verse': verse.verse,
            'tzotzil_text': verse.tzotzil_text,
            'spanish_text': verse.spanish_text
        } for verse in results]

        logger.info(f"Búsqueda completada. Encontrados {len(results_dict)} resultados")
        return render_template('search_results.html',
                             results=results_dict,
                             keyword=keyword,
                             versions=versions,
                             testament=testament,
                             book=book,
                             books=books)

    except Exception as e:
        logger.error(f"Error en la búsqueda: {str(e)}")
        return render_template('error.html',
                             error="Ocurrió un error durante la búsqueda. Por favor, intente nuevamente."), 500


@routes.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        try:
            data = request.get_json()
            setting_type = data.get('type')

            db = get_db()
            cur = db.cursor()

            if setting_type == 'profile':
                cur.execute(
                    """
                    UPDATE users 
                    SET first_name = ?, phone = ? 
                    WHERE id = ?
                """, (data.get('name', current_user.first_name),
                      data.get('phone', current_user.phone), current_user.id))
                db.commit()
                return jsonify({
                    'status': 'success',
                    'message': 'Profile updated successfully'
                })

            elif setting_type == 'appearance':
                session['dark_mode'] = data.get('dark_mode', False)
                session['font_size'] = data.get('font_size', 16)
                return jsonify({
                    'status': 'success',
                    'message': 'Appearance settings updated'
                })

            elif setting_type == 'reading':
                session['verse_numbers'] = data.get('verse_numbers', True)
                session['parallel_view'] = data.get('parallel_view', True)
                session['primary_language'] = data.get('primary_language',
                                                       'tzotzil')
                return jsonify({
                    'status': 'success',
                    'message': 'Reading preferences updated'
                })

            elif setting_type == 'language':
                session['language'] = data.get('language', 'es')
                session['bilingual_mode'] = data.get('bilingual_mode', True)
                return jsonify({
                    'status': 'success',
                    'message': 'Language preferences updated'
                })

            return jsonify({
                'status': 'error',
                'message': 'Invalid setting type'
            })

        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # GET request - render settings page
    try:
        return render_template('settings.html',
                               books=get_sorted_books(),
                               user=current_user)
    except Exception as e:
        logger.error(f"Error loading settings page: {str(e)}")
        return render_template('error.html',
                               error="Error loading settings"), 500


@routes.route('/get_chapters/<book>')
def get_chapters(book):
    """Obtiene los capítulos de un libro con manejo de errores mejorado y caché"""
    try:
        logger.info(f"Solicitando capítulos para el libro: {book}")
        
        # Usar el gestor de base de datos con caché
        chapters_result = db_manager.get_verses(book)
        
        if not chapters_result['success']:
            logger.error(f"Error obteniendo capítulos: {chapters_result['error']}")
            return jsonify({
                'error': 'Error obteniendo capítulos',
                'message': chapters_result['error']
            }), 500
            
        chapters = chapters_result['data']['chapters']
        if not chapters:
            logger.warning(f"No se encontraron capítulos para el libro {book}")
            return jsonify({
                'error': 'No hay capítulos disponibles',
                'message': f"No se encontraron capítulos para {book}"
            }), 404
            
        logger.info(f"Retornando {len(chapters)} capítulos para {book}")
        return jsonify(chapters)
        
    except Exception as e:
        error_msg = f"Error obteniendo capítulos para {book}: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Error procesando la solicitud'
        }), 500


@routes.route('/validate', methods=['POST'])
def validate():
    """Validate data based on the request body"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        validation_type = data.get('type')
        if not validation_type:
            return jsonify({'error': 'Missing validation type'}), 400

        if validation_type == 'bible_verse':
            book = data.get('book')
            chapter = data.get('chapter')
            verse = data.get('verse')
            tzotzil_text = data.get('tzotzil_text')
            spanish_text = data.get('spanish_text')

            errors = validator.validate_bible_verse(book, chapter, verse,
                                                    tzotzil_text, spanish_text)

            if errors:
                return jsonify({'status': 'error', 'errors': errors}), 400
            else:
                return jsonify({'status': 'success'}), 200

        elif validation_type == 'user_data':
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')

            errors = validator.validate_user_data(email, username, password)

            if errors:
                return jsonify({'status': 'error', 'errors': errors}), 400
            else:
                return jsonify({'status': 'success'}), 200

        else:
            return jsonify({'error': 'Invalid validation type'}), 400

    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

def get_db():
    """Get database session using the database manager"""
    return db_manager.get_session()
from seminar_generator import SeminarGenerator

@routes.route('/generate_seminar', methods=['POST'])
def generate_seminar():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        audience = data.get('audience', 'general')
        duration = data.get('duration', '60min')
        
        generator = SeminarGenerator()
        seminar = generator.generate_seminar(topic, audience, duration)
        
        # Generar PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"seminar_{timestamp}.pdf"
        seminars_dir = os.path.join(current_app.static_folder, 'seminars')
        os.makedirs(seminars_dir, exist_ok=True)
        
        pdf_path = os.path.join(seminars_dir, filename)
        if generator.export_to_pdf(seminar, pdf_path):
            pdf_url = url_for('static', filename=f'seminars/{filename}')
            return jsonify({
                'success': True,
                'seminar': seminar,
                'pdf_url': pdf_url
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error generating PDF'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in generate_seminar: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
