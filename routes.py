from flask import Blueprint, request, Flask, jsonify, render_template, redirect, url_for, g, session, flash
from flask_login import login_required, current_user
from auth import token_required
from database import db_manager, get_db
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import text, func
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
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)
routes = Blueprint('routes', __name__)

def init_routes(app):
    """Inicializar y registrar las rutas en la aplicación"""
    try:
        logger.info("Registrando rutas principales...")
        app.register_blueprint(routes)
        return True
    except Exception as e:
        logger.error(f"Error al registrar rutas: {str(e)}")
        return False

logger = logging.getLogger(__name__)
routes = Blueprint('routes', __name__)

def init_routes(app):
    """Inicializar y registrar las rutas en la aplicación"""
    try:
        logger.info("Registrando rutas principales...")
        app.register_blueprint(routes)
        return True
    except Exception as e:
        logger.error(f"Error al registrar rutas: {str(e)}")
        return False
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


@routes.route('/daily_promise', methods=['GET'])
def daily_promise():
    try:
        # Obtener la fecha actual en UTC
        today = datetime.utcnow().date()

        # Usar el día del año como semilla para obtener una promesa consistente
        day_of_year = today.timetuple().tm_yday

        # Contar total de promesas
        total_promises = db.session.query(Promise).count()
        if total_promises == 0:
            logger.warning("No hay promesas disponibles en la base de datos")
            return jsonify({
                'status': 'error',
                'message': 'No hay promesas disponibles'
            }), 404

        # Usar el módulo para obtener un índice consistente para el día
        promise_index = day_of_year % total_promises

        # Obtener la promesa del día
        daily_promise = db.session.query(Promise).offset(promise_index).limit(1).first()

        if not daily_promise:
            logger.error("Error al obtener la promesa diaria")
            return jsonify({
                'status': 'error',
                'message': 'Error al obtener la promesa diaria'
            }), 500

        return jsonify({
            'status': 'success',
            'verse_text': daily_promise.verse_text,
            'background_image': daily_promise.background_image,
            'book_reference': daily_promise.book_reference,
            'date': today.isoformat()
        })

    except Exception as e:
        logger.error(f"Error al obtener la promesa diaria: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error al obtener la promesa diaria'
        }), 500

@routes.route('/random_promise')
def random_promise():
    try:
        random_promise = db.session.query(Promise).order_by(func.random()).first()

        if not random_promise:
            logger.warning("No hay promesas disponibles en la base de datos")
            return jsonify({
                'status': 'error',
                'message': 'No hay promesas disponibles'
            }), 404

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
@cross_origin()
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
        verses_result = db_manager.get_verses(book, str(chapter))

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
                                 book='all')

        keyword = request.args.get('keyword', '').strip()
        versions = request.args.getlist('version') or ['tzotzil', 'spanish']
        book = request.args.get('book', 'all')

        # Usar SQLAlchemy para la consulta
        from models import BibleVerse
        query = BibleVerse.query

        if book != 'all':
            query = query.filter(BibleVerse.book == book)

        # Construir condiciones de búsqueda
        search_conditions = []
        if 'tzotzil' in versions:
            search_conditions.append(BibleVerse.tzotzil_text.ilike(f'%{keyword}%'))
        if 'spanish' in versions:
            search_conditions.append(BibleVerse.spanish_text.ilike(f'%{keyword}%'))

        if search_conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*search_conditions))

        try:
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
                                book=book,
                                books=books)

        except Exception as e:
            logger.error(f"Error en la búsqueda: {str(e)}")
            return render_template('error.html',
                                error="Error al realizar la búsqueda. Por favor, intente nuevamente."), 500

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
def settings():
    """Maneja las configuraciones del usuario"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                logger.error("No se proporcionaron datos en la solicitud POST")
                return jsonify({'status': 'error', 'message': 'No data provided'}), 400

            if not isinstance(data, dict):
                logger.error("Datos proporcionados en formato inválido")
                return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400

            setting_type = data.get('type')
            if not setting_type:
                return jsonify({'status': 'error', 'message': 'Setting type required'}), 400

            if setting_type == 'profile':
                try:
                    # Simular actualización de perfil sin base de datos de usuarios
                    name = data.get('name', '')
                    phone = data.get('phone', '')
                    
                    # Guardar en sesión para persistencia temporal
                    session['user_name'] = name
                    session['user_phone'] = phone
                    
                    return jsonify({
                        'status': 'success',
                        'message': 'Perfil actualizado exitosamente'
                    })
                except Exception as e:
                    logger.error(f"Error updating profile: {str(e)}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Error actualizando el perfil'
                    }), 500

            elif setting_type == 'appearance':
                try:
                    session['dark_mode'] = data.get('dark_mode', False)
                    session['font_size'] = data.get('font_size', 16)
                    return jsonify({
                        'status': 'success',
                        'message': 'Appearance settings updated'
                    })
                except Exception as e:
                    logger.error(f"Error updating appearance: {str(e)}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Error updating appearance settings'
                    }), 500

            elif setting_type == 'reading':
                try:
                    session['verse_numbers'] = data.get('verse_numbers', True)
                    session['parallel_view'] = data.get('parallel_view', True)
                    session['primary_language'] = data.get('primary_language', 'tzotzil')
                    logger.info(f"Updated reading preferences for user {current_user.id}")
                    return jsonify({
                        'status': 'success',
                        'message': 'Reading preferences updated'
                    })
                except Exception as e:
                    logger.error(f"Error updating reading preferences: {str(e)}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Error updating reading preferences'
                    }), 500

            elif setting_type == 'language':
                try:
                    session['language'] = data.get('language', 'es')
                    session['bilingual_mode'] = data.get('bilingual_mode', True)
                    return jsonify({
                        'status': 'success',
                        'message': 'Language preferences updated'
                    })
                except Exception as e:
                    logger.error(f"Error updating language settings: {str(e)}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Error updating language settings'
                    }), 500

            return jsonify({
                'status': 'error',
                'message': 'Invalid setting type'
            }), 400

        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # GET request
    try:
        return render_template('settings.html',
                             books=get_sorted_books())
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
        verses_result = db_manager.get_verses(book)

        if not verses_result['success']:
            logger.error(f"Error obteniendo capítulos: {verses_result['error']}")
            return jsonify({
                'error': 'Error obteniendo capítulos',
                'message': verses_result['error']
            }), 500

        chapters = verses_result['data'].get('chapters', [])
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
@login_required
def validate_data():
    """Validate data based on the request body"""
    try:
        data = request.get_json()
        if not data:
            logger.warning("Validation attempt with empty request body")
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

        success, signed_url = generator.export_to_pdf(seminar, filename)
        if success:
            return jsonify({
                'success': True,
                'seminar': seminar,
                'pdf_url': signed_url
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

@routes.route('/download_seminar/<filename>')
def download_seminar(filename):
    try:
        storage_client = Client()
        # Verificar si el archivo existe
        if not storage_client.exists(filename):
            return jsonify({
                'success': False,
                'error': 'Archivo no encontrado'
            }), 404

        # Generar URL de descarga temporal
        download_url = storage_client.get_download_url(filename, expire_in=3600)

        return jsonify({
            'success': True,
            'download_url': download_url
        })

    except Exception as e:
        current_app.logger.error(f"Error obteniendo URL de descarga: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando enlace de descarga'
        }), 500
@routes.route('/subscription')
@token_required
def subscription_portal(current_user):
    return render_template('subscription.html', user=current_user)

@routes.route('/donate/<amount>')
def donate(amount):
    """Maneja las donaciones y redirecciona a PayPal"""
    try:
        logger.info(f"Iniciando proceso de donación - IP: {request.remote_addr}")
        logger.info(f"Monto solicitado: ${amount}")

        try:
            amount = float(amount)
        except ValueError:
            logger.error(f"Error de conversión - monto inválido: {amount}")
            flash('Monto inválido', 'error')
            return jsonify({'error': 'Monto inválido'}), 400

        if amount <= 0:
            logger.warning(f"Monto inválido detectado: ${amount}")
            flash('Por favor ingrese un monto válido', 'error')
            return jsonify({'error': 'Monto debe ser mayor a 0'}), 400

        # Usar el enlace de donación de PayPal
        paypal_link = "https://www.paypal.com/donate/?hosted_button_id=ZZT98YTR4YCXE"
        logger.info(f"URL de PayPal generada: {paypal_link}")

        # Registrar detalles adicionales
        logger.info(f"User Agent: {request.user_agent}")
        logger.info(f"Tipo de solicitud: {'AJAX' if request.headers.get('X-Requested-With') else 'Normal'}")

        # Retornar JSON para solicitudes AJAX o redirección para solicitudes normales
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.info("Respondiendo con JSON para solicitud AJAX")
            return jsonify({'redirect_url': paypal_link, 'amount': amount})

        logger.info("Redirigiendo directamente a PayPal")
        return redirect(paypal_link)

    except ValueError as e:
        logger.error(f"Error procesando donación: {str(e)}")
        flash('Monto inválido', 'error')
        return redirect(url_for('routes.settings'))
    except Exception as e:
        logger.error(f"Error inesperado procesando donación: {str(e)}")
        flash('Error procesando la donación', 'error')
        return redirect(url_for('routes.settings'))

@routes.route('/donation/success')
def donation_success():
    """Página de agradecimiento por la donación"""
    return render_template('donation_success.html')

@routes.route('/privacy')
def privacy():
    """Página de política de privacidad"""
    return render_template('privacy.html')

@routes.route('/check_subscription')
@token_required
def check_subscription(current_user):
    """Verifica y actualiza el estado de la suscripción"""
    try:
        if current_user.subscription_status == 'active':
            # Verificar pagos aquí
            if payment_overdue:  # Implementar lógica de verificación
                current_user.plan_type = 'Free'
                current_user.subscription_status = 'inactive'
                current_user.nevin_access = False
                db.session.commit()

        return jsonify(current_user.to_dict())
    except Exception as e:
        logger.error(f"Error checking subscription: {str(e)}")
        return jsonify({'error': 'Error checking subscription'}), 500

# API Endpoints Documentation
"""
Base URL: /api
Authentication: JWT token required for most endpoints

Available endpoints:
- POST /api/validate: Validates input data
- GET /api/books: Returns list of available books
- GET /api/chapters/{book}: Returns chapters for a specific book
- GET /api/verses/{book}/{chapter}: Returns verses for a specific chapter
- POST /api/settings: Updates user settings
"""

@routes.route('/api/bible/books', methods=['GET'])
@cross_origin()
def get_books_api():
    try:
        books = get_sorted_books()
        return jsonify(books), 200
    except Exception as e:
        logger.error(f"Error getting books: {str(e)}")
        return jsonify({'error': 'Error retrieving books'}), 500

@routes.route('/api/bible/chapters/<book>', methods=['GET'])
@cross_origin()
def get_chapters_api(book):
    try:
        verses_result = db_manager.get_verses(book)
        if not verses_result['success']:
            return jsonify({'error': verses_result['error']}), 500
        return jsonify(verses_result['data']), 200
    except Exception as e:
        logger.error(f"Error getting chapters: {str(e)}")
        return jsonify({'error': 'Error retrieving chapters'}), 500

@routes.route('/api/bible/verses/<book>/<int:chapter>', methods=['GET'])
@cross_origin()
def get_verses_api(book, chapter):
    try:
        verses_result = db_manager.get_verses(book, str(chapter))
        if not verses_result['success']:
            return jsonify({'error': verses_result['error']}), 500
        return jsonify(verses_result['data']), 200
    except Exception as e:
        logger.error(f"Error getting verses: {str(e)}")
        return jsonify({'error': 'Error retrieving verses'}), 500

@routes.route('/api/validate', methods=['POST'])
@login_required
def validate():
    """
    Validates input data

    Request body:
    {
        "type": "bible_verse|user_data",
        "data": {
            // Data fields depending on type
        }
    }

    Returns:
        200: Validation successful
        400: Invalid data with error details
        401: Unauthorized
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Validation attempt with empty request body")
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
@routes.route('/download_bible')
def download_bible():
    """Descarga la base de datos bíblica para uso offline"""
    try:
        from database_export import export_bible_data
        db_path = export_bible_data()

        return send_file(
            db_path,
            as_attachment=True,
            download_name=f"biblia_tzotzil_{datetime.now().strftime('%Y%m%d')}.db",
            mimetype='application/x-sqlite3'
        )

    except Exception as e:
        logger.error(f"Error en descarga: {str(e)}")
        return jsonify({
            'error': 'Error generando archivo de descarga'
        }), 500