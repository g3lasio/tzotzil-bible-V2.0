
from flask import Flask, jsonify
from flask_cors import CORS
from database import db_manager
from routes import init_routes
import logging

app = Flask(__name__)
CORS(app)

# Import error handlers
from error_handlers import register_error_handlers
register_error_handlers(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    init_routes(app)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
