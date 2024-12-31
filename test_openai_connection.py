
import os
import logging
from openai import OpenAI
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai_connection():
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="Test de conexión"
        )
        if response.data:
            logger.info("Conexión con OpenAI verificada exitosamente")
            return True
    except Exception as e:
        logger.error(f"Error conectando con OpenAI: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()
