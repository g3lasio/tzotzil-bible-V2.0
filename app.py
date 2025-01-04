
import os
import logging
from __init__ import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app = create_app()
    if app:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.error("No se pudo iniciar la aplicación")
