"""
CacheManager - Sistema de caché multinivel con Redis
"""
import logging
import json
from typing import Any, Optional, Union
from datetime import datetime, timedelta
from functools import wraps
import redis
from cachetools import TTLCache

# Configuración de logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor de caché multinivel con Redis."""

    def __init__(self, redis_url: Optional[str] = None):
        """
        Inicializa el gestor de caché.

        Args:
            redis_url: URL de conexión a Redis
        """
        self.local_cache = TTLCache(maxsize=1000, ttl=300)  # Caché L1: 5 minutos
        self.redis = None
        self._initialized = False
        if redis_url:
            self.init_redis(redis_url)

    def init_redis(self, redis_url: str) -> bool:
        """
        Inicializa la conexión a Redis con manejo de errores.

        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            if self._initialized:
                logger.warning("Redis ya fue inicializado")
                return True

            self.redis = redis.from_url(
                redis_url,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                retry_on_timeout=True
            )
            self.redis.ping()  # Verificar conexión
            self._initialized = True
            logger.info("Conexión a Redis establecida exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error conectando a Redis: {str(e)}")
            self.redis = None
            logger.warning("Funcionando en modo degradado con solo caché local")
            return False

    def ping(self) -> bool:
        """
        Verifica el estado de la conexión.

        Returns:
            bool: True si el caché está funcionando (local o Redis), False en caso contrario
        """
        try:
            if self.redis:
                self.redis.ping()
                return True
            return True  # Caché local siempre disponible
        except Exception:
            logger.warning("Redis no disponible, usando caché local")
            self.redis = None
            return True  # Retorna True porque el caché local sigue funcionando

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché (L1 -> L2).

        Args:
            key: Clave a buscar

        Returns:
            Valor almacenado o None si no existe
        """
        try:
            # Buscar en caché L1
            if key in self.local_cache:
                logger.debug(f"Cache hit L1: {key}")
                return self.local_cache[key]

            # Buscar en Redis (L2) si está disponible
            if self.redis:
                try:
                    value = self.redis.get(key)
                    if value:
                        try:
                            decoded_value = json.loads(value)
                            self.local_cache[key] = decoded_value  # Actualizar L1
                            logger.debug(f"Cache hit L2: {key}")
                            return decoded_value
                        except json.JSONDecodeError:
                            logger.warning(f"Error decodificando valor de Redis para {key}")
                            self.delete(key)  # Eliminar valor corrupto
                except redis.RedisError as e:
                    logger.warning(f"Error de Redis al obtener {key}: {str(e)}")
                    self.redis = None  # Desactivar Redis temporalmente

            logger.debug(f"Cache miss: {key}")
            return None

        except Exception as e:
            logger.error(f"Error obteniendo de caché: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Almacena un valor en el caché (L1 y L2).

        Args:
            key: Clave
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos

        Returns:
            True si se almacenó correctamente en al menos un nivel
        """
        success = False
        try:
            # Almacenar en caché L1
            self.local_cache[key] = value
            success = True

            # Almacenar en Redis (L2) si está disponible
            if self.redis:
                try:
                    encoded_value = json.dumps(value)
                    self.redis.setex(key, ttl, encoded_value)
                    logger.debug(f"Valor almacenado en L1 y L2: {key}")
                except (TypeError, json.JSONDecodeError, redis.RedisError) as e:
                    logger.warning(f"Error almacenando en Redis: {str(e)}")
                    self.redis = None  # Desactivar Redis temporalmente

            return success

        except Exception as e:
            logger.error(f"Error almacenando en caché: {str(e)}")
            return success

    def delete(self, key: str) -> bool:
        """
        Elimina una clave del caché.

        Args:
            key: Clave a eliminar

        Returns:
            True si se eliminó correctamente de al menos un nivel
        """
        success = False
        try:
            # Eliminar de L1
            self.local_cache.pop(key, None)
            success = True

            # Eliminar de Redis (L2) si está disponible
            if self.redis:
                try:
                    self.redis.delete(key)
                    logger.debug(f"Clave eliminada de L1 y L2: {key}")
                except redis.RedisError as e:
                    logger.warning(f"Error eliminando de Redis: {str(e)}")
                    self.redis = None  # Desactivar Redis temporalmente

            return success

        except Exception as e:
            logger.error(f"Error eliminando de caché: {str(e)}")
            return success

    def clear(self) -> bool:
        """
        Limpia todo el caché.

        Returns:
            True si se limpió correctamente de al menos un nivel
        """
        success = False
        try:
            # Limpiar L1
            self.local_cache.clear()
            success = True

            # Limpiar Redis (L2) si está disponible
            if self.redis:
                try:
                    self.redis.flushdb()
                    logger.info("Caché limpiado completamente")
                except redis.RedisError as e:
                    logger.warning(f"Error limpiando Redis: {str(e)}")
                    self.redis = None  # Desactivar Redis temporalmente

            return success

        except Exception as e:
            logger.error(f"Error limpiando caché: {str(e)}")
            return success

    def cached(self, ttl: int = 3600):
        """
        Decorador para cachear resultados de funciones.

        Args:
            ttl: Tiempo de vida en segundos del valor en caché

        Returns:
            Decorador que maneja el cacheo de la función
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Generar clave única para la función y sus argumentos
                    cache_key = f"{func.__module__}:{func.__name__}:{hash(str(args))}"
                    if kwargs:
                        cache_key += f":{hash(str(sorted(kwargs.items())))}"

                    # Intentar obtener del caché
                    cached_value = self.get(cache_key)
                    if cached_value is not None:
                        logger.debug(f"Cache hit para función {func.__name__}")
                        return cached_value

                    # Ejecutar función y almacenar resultado
                    result = func(*args, **kwargs)
                    if result is not None:  # Solo cachear resultados no nulos
                        self.set(cache_key, result, ttl)
                        logger.debug(f"Resultado cacheado para función {func.__name__}")
                    return result

                except Exception as e:
                    logger.error(f"Error en decorador cache para {func.__name__}: {str(e)}")
                    # En caso de error, ejecutar la función sin cacheo
                    return func(*args, **kwargs)
            return wrapper
        return decorator

# Instancia global del gestor de caché
cache_manager = CacheManager()