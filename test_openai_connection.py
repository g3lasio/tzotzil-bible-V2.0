import logging
from azure_openai_config import openai_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai_connection():
    """Prueba la conexión con OpenAI y verifica las respuestas."""
    try:
        # 1. Probar creación de embeddings
        logger.info("Probando generación de embeddings...")
        test_text = "¿Qué significa el bautismo según la Biblia?"
        embedding = openai_config.create_embedding(test_text)
        
        if embedding:
            logger.info("✅ Generación de embeddings exitosa")
            logger.info(f"Dimensiones del embedding: {len(embedding)}")
        else:
            logger.error("❌ Error generando embeddings")
            return False

        # 2. Probar completion
        logger.info("\nProbando generación de respuestas...")
        response = openai_config.create_completion(test_text)
        
        if response:
            logger.info("✅ Generación de respuesta exitosa")
            logger.info(f"Respuesta recibida: {response[:100]}...")
        else:
            logger.error("❌ Error generando respuesta")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Error en la prueba de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🔄 Iniciando prueba de conexión con OpenAI...")
    
    success = test_openai_connection()
    if success:
        logger.info("\n✅ Todas las pruebas completadas exitosamente")
    else:
        logger.error("\n❌ Las pruebas fallaron, verifica la configuración y los logs")
