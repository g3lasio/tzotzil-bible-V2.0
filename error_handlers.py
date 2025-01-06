
from flask import jsonify
import logging
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(e):
        logger.error(f"Token inválido: {str(e)}")
        return jsonify({"error": "Token inválido"}), 401

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token(e):
        logger.error(f"Token expirado: {str(e)}")
        return jsonify({"error": "Token expirado"}), 401

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        logger.error(f"Error de base de datos: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        logger.error(f"Error HTTP: {str(e)}")
        return jsonify({"error": str(e.description)}), e.code

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        logger.error(f"Error no manejado: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
