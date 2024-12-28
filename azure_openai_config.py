import os
import logging
import time
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Constantes
MODEL_NAME = "gpt-4"
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 2
MAX_RETRY_DELAY = 30
MAX_REQUESTS_PER_MINUTE = 20  # Reducido para mayor seguridad
BATCH_SIZE = 5  # Reducido para mejor control
MIN_PAUSE_BETWEEN_BATCHES = 3  # Aumentado para dar más espacio entre lotes
MAX_REQUESTS_PER_BATCH = 5  # Máximo de solicitudes por lote
RATE_LIMIT_PAUSE = 60  # Pausa en segundos cuando se alcanza el límite

class OpenAIConfig:
    """Configuración mejorada de OpenAI con manejo de errores y control de rate limit."""
    
    def __init__(self):
        """Inicializa el cliente de OpenAI con control de rate limit."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")
            
        self.client = self._initialize_client()
        self._request_count = 0
        self._last_request_time = time.time()
        self._batch_start_time = time.time()
        logger.info("Cliente OpenAI inicializado correctamente")
        
    def _initialize_client(self) -> OpenAI:
        """Inicializa el cliente de OpenAI con manejo de errores."""
        try:
            return OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Error inicializando cliente OpenAI: {str(e)}")
            raise

    def get_client(self) -> OpenAI:
        """Retorna el cliente OpenAI inicializado."""
        return self.client

    def _manage_rate_limit(self):
        """Gestiona el rate limit de las solicitudes a OpenAI con controles estrictos."""
        current_time = time.time()
        time_diff = current_time - self._last_request_time
        batch_time_diff = current_time - self._batch_start_time
        
        # Control de ventana deslizante por minuto
        if time_diff >= 60:
            logger.info("Reiniciando contadores de rate limit")
            self._request_count = 0
            self._last_request_time = current_time
            self._batch_start_time = current_time
            
        # Control estricto de rate limit
        if self._request_count >= MAX_REQUESTS_PER_MINUTE:
            sleep_time = RATE_LIMIT_PAUSE
            logger.warning(f"Rate limit alcanzado. Pausa de seguridad de {sleep_time} segundos...")
            time.sleep(sleep_time)
            self._request_count = 0
            self._last_request_time = time.time()
            self._batch_start_time = time.time()
            return
            
        # Control por lote
        if self._request_count % MAX_REQUESTS_PER_BATCH == 0 and self._request_count > 0:
            batch_sleep = max(MIN_PAUSE_BETWEEN_BATCHES, 
                            MIN_PAUSE_BETWEEN_BATCHES - batch_time_diff)
            logger.info(f"Pausa entre lotes: {batch_sleep:.2f}s")
            time.sleep(batch_sleep)
            self._batch_start_time = time.time()
            
        # Pausa mínima entre solicitudes individuales
        if time_diff < 1.0:  # Asegurar al menos 1 segundo entre solicitudes
            time.sleep(1.0 - time_diff)
            
        self._request_count += 1
        self._last_request_time = time.time()
        
        logger.debug(f"Solicitudes en el último minuto: {self._request_count}/{MAX_REQUESTS_PER_MINUTE}")

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=INITIAL_RETRY_DELAY, max=MAX_RETRY_DELAY),
        reraise=True
    )
    def create_embedding(self, text: str) -> Optional[list]:
        """
        Crea un embedding con reintentos y manejo inteligente de rate limit.
        
        Args:
            text: Texto para generar embedding
            
        Returns:
            Lista de flotantes representando el embedding o None si hay error
        """
        self._manage_rate_limit()
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
            
        except OpenAIError as e:
            if "insufficient_quota" in str(e):
                logger.error("Error de cuota de OpenAI excedida. Por favor, verifica tu plan y facturación.")
                time.sleep(60)  # Esperar un minuto antes de reintentar
            elif "rate_limit_exceeded" in str(e):
                logger.warning("Rate limit excedido, esperando antes de reintentar...")
                time.sleep(20)  # Esperar 20 segundos antes de reintentar
            else:
                logger.error(f"Error de OpenAI: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado generando embedding: {str(e)}")
            return None

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=INITIAL_RETRY_DELAY, max=MAX_RETRY_DELAY),
        reraise=True
    )
    def create_completion(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Crea una completion con reintentos y manejo de errores.
        
        Args:
            prompt: Texto del prompt
            max_tokens: Número máximo de tokens en la respuesta
            
        Returns:
            Texto de la respuesta o None si hay error
        """
        self._manage_rate_limit()
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
            
        except OpenAIError as e:
            if "insufficient_quota" in str(e):
                logger.error("Error de cuota de OpenAI excedida. Por favor, verifica tu plan y facturación.")
                time.sleep(60)
            elif "rate_limit_exceeded" in str(e):
                logger.warning("Rate limit excedido, esperando antes de reintentar...")
                time.sleep(20)
            else:
                logger.error(f"Error de OpenAI: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado en completion: {str(e)}")
            return None

# Instanciar la configuración
openai_config = OpenAIConfig()
