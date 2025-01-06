
from flask import jsonify
import logging
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DatabaseError
from werkzeug.exceptions import HTTPException
from flask_cors import CrossOriginResourceSharing

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(e):
        logger.error(f"Token inválido: {str(e)}")
        return jsonify({
            "error": "Token inválido",
            "details": str(e),
            "code": "AUTH001"
        }), 401

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token(e):
        logger.error(f"Token expirado: {str(e)}")
        return jsonify({
            "error": "Token expirado",
            "details": "Por favor inicie sesión nuevamente",
            "code": "AUTH002"
        }), 401

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        logger.error(f"Error de base de datos: {str(e)}")
        if isinstance(e, IntegrityError):
            return jsonify({
                "error": "Error de integridad en la base de datos",
                "code": "DB001"
            }), 409
        return jsonify({
            "error": "Error interno del servidor",
            "code": "DB002"
        }), 500

    @app.errorhandler(DatabaseError)
    def handle_database_error(e):
        logger.error(f"Error crítico de base de datos: {str(e)}")
        return jsonify({
            "error": "Error de conexión con la base de datos",
            "code": "DB003"
        }), 503

    @app.errorhandler(CrossOriginResourceSharing.error_response)
    def handle_cors_error(e):
        logger.error(f"Error CORS: {str(e)}")
        return jsonify({
            "error": "Error de acceso cruzado",
            "code": "CORS001"
        }), 403

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        logger.error(f"Error HTTP: {str(e)}")
        return jsonify({
            "error": str(e.description),
            "code": f"HTTP{e.code}"
        }), e.code

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        logger.error(f"Error no manejado: {str(e)}")
        return jsonify({
            "error": "Error interno del servidor",
            "details": str(e) if app.debug else None,
            "code": "SYS001"
        }), 500
