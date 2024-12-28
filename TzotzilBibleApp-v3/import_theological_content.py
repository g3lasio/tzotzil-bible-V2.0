import os
import json
import time
import logging
from datetime import datetime
from psycopg2.extras import Json
from openai import OpenAI
import psycopg2

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constantes y configuración
MAX_RETRIES = 3
BATCH_SIZE = 8  # Aumentado para mejor velocidad
EMBEDDING_BATCH_SIZE = 10
PAUSE_BETWEEN_BATCHES = 3  # segundos
PAUSE_BETWEEN_EMBEDDINGS = 1  # segundos
MIN_CONTENT_LENGTH = 50
MAX_CONTENT_LENGTH = 8000

def get_embedding(text: str, client, max_retries: int = MAX_RETRIES):
    """
    Obtiene el embedding para un texto con reintentos y manejo de rate limit.
    
    Args:
        text: Texto para generar embedding
        client: Cliente de OpenAI
        max_retries: Número máximo de reintentos
    """
    base_wait_time = 5  # Tiempo base de espera en segundos
    
    for attempt in range(max_retries):
        try:
            # Verificar si ya se alcanzó el límite de solicitudes
            if attempt > 0:
                exponential_wait = base_wait_time * (2 ** (attempt - 1))
                logger.info(f"Intento {attempt + 1}/{max_retries}. "
                          f"Esperando {exponential_wait} segundos...")
                time.sleep(exponential_wait)
            
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "rate_limit" in error_msg:
                wait_time = min(60, base_wait_time * (2 ** attempt))
                logger.warning(
                    f"Rate limit alcanzado en intento {attempt + 1}/{max_retries}. "
                    f"Esperando {wait_time} segundos...")
                time.sleep(wait_time)
                
            elif "insufficient_quota" in error_msg:
                logger.error(
                    "Cuota de OpenAI excedida. "
                    "Esperando 120 segundos antes de reintentar...")
                time.sleep(120)
                
            elif "invalid_request_error" in error_msg:
                logger.error(f"Error de solicitud inválida: {str(e)}")
                return None  # No reintentar errores de solicitud inválida
                
            else:
                logger.error(
                    f"Error desconocido al obtener embedding "
                    f"(intento {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    return None
            continue
            
    logger.error(f"No se pudo obtener embedding después de {max_retries} intentos")
    return None

def update_progress(cur, book_name, total_pages, processed_pages, status='processing', 
                   error_message=None, checkpoint=None):
    """
    Actualizar el progreso de procesamiento con checkpoint para recuperación.
    
    Args:
        cur: Cursor de la base de datos
        book_name: Nombre del libro
        total_pages: Total de páginas
        processed_pages: Páginas procesadas
        status: Estado actual del proceso
        error_message: Mensaje de error si existe
        checkpoint: Datos de checkpoint para recuperación
    """
    try:
        cur.execute("""
            INSERT INTO progress_tracking (
                book_name, 
                total_pages, 
                processed_pages, 
                status, 
                error_message,
                checkpoint_data,
                last_update
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (book_name) DO UPDATE
            SET processed_pages = %s,
                status = %s,
                error_message = %s,
                checkpoint_data = %s,
                last_update = CURRENT_TIMESTAMP
        """, (
            book_name, total_pages, processed_pages, status, error_message, 
            Json(checkpoint) if checkpoint else None,
            processed_pages, status, error_message,
            Json(checkpoint) if checkpoint else None
        ))
        
        # Log detallado del progreso
        completion_rate = (processed_pages / total_pages * 100) if total_pages > 0 else 0
        logger.info(
            f"Progreso actualizado - Libro: {book_name} | "
            f"Progreso: {processed_pages}/{total_pages} ({completion_rate:.1f}%) | "
            f"Estado: {status}"
        )
        
    except Exception as e:
        logger.error(
            f"Error actualizando progreso para {book_name}: {str(e)}\n"
            f"Detalles - Páginas: {processed_pages}/{total_pages}, Estado: {status}"
        )

# Caché simple para embeddings
embedding_cache = {}

def get_content_hash(content):
    """Genera un hash simple para el contenido."""
    return hash(content.strip().lower())

def process_content_batch(batch, client):
    """
    Procesa un lote de contenido para obtener embeddings con caché y control de rate.
    
    Args:
        batch: Lista de registros a procesar
        client: Cliente de OpenAI
        
    Returns:
        Lista de tuplas (registro, embedding)
    """
    processed_records = []
    batch_size = len(batch)
    
    logger.info(f"Procesando lote de {batch_size} registros...")
    
    for idx, record in enumerate(batch, 1):
        try:
            content = record['content']
            content_hash = get_content_hash(content)
            
            # Verificar caché
            if content_hash in embedding_cache:
                logger.info(f"Usando embedding cacheado para: {record['title']}")
                processed_records.append((record, embedding_cache[content_hash]))
                continue
                
            # Obtener nuevo embedding
            embedding = get_embedding(content, client, max_retries=MAX_RETRIES)
            if embedding:
                embedding_cache[content_hash] = embedding
                processed_records.append((record, embedding))
                logger.info(f"Embedding generado exitosamente para: {record['title']}")
            else:
                logger.error(f"No se pudo obtener embedding para: {record['title']}")
                
            # Pausa controlada entre registros
            if idx < batch_size:  # No pausar después del último registro
                logger.debug(f"Pausa de {PAUSE_BETWEEN_EMBEDDINGS}s entre embeddings...")
                time.sleep(PAUSE_BETWEEN_EMBEDDINGS)
                
        except Exception as e:
            logger.error(f"Error procesando registro {record['title']}: {str(e)}")
            continue
    
    # Pausa más larga entre lotes
    logger.info(f"Lote completado. Pausa de {PAUSE_BETWEEN_BATCHES}s antes del siguiente lote...")
    time.sleep(PAUSE_BETWEEN_BATCHES)
    
    return processed_records

def init_database(cur):
    """Inicializa las tablas necesarias para el proceso de importación."""
    try:
        # Crear tabla de progreso con soporte para checkpoints
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progress_tracking (
                book_name TEXT PRIMARY KEY,
                total_pages INTEGER NOT NULL,
                processed_pages INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                checkpoint_data JSONB,
                last_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla para contenido teológico si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS theological_content (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                metadata JSONB,
                embedding VECTOR(1536)
            )
        """)
        
        logger.info("Tablas inicializadas correctamente")
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {str(e)}")
        raise

def process_json_content(file_path):
    """
    Procesa el contenido de un archivo JSON.
    
    Args:
        file_path: Ruta al archivo JSON
    """
    try:
        with open(os.path.join('EGW BOOKS', file_path), 'r', encoding='utf-8') as file:
            data = json.load(file)
            records = []
            book_name = os.path.basename(file_path).replace('.json', '')
            current_batch = []
            
            logger.info(f"Iniciando procesamiento de {book_name}")
            total_pages = len(data)
            processed = 0
            
            # Procesar cada página del libro
            for page_data in data:
                try:
                    page_num = page_data.get('page', 0)
                    content_list = page_data.get('content', [])
                    
                    # Unir el contenido de la página
                    content_text = ' '.join(str(item) for item in content_list)
                    
                    # Validar contenido
                    if content_text and len(content_text.strip()) > MIN_CONTENT_LENGTH:
                        record = {
                            'title': f"{book_name} - Página {page_num}",
                            'content': content_text[:MAX_CONTENT_LENGTH],
                            'source': book_name,
                            'metadata': {
                                'type': 'egw',
                                'page': page_num,
                                'book': book_name,
                                'content_length': len(content_text),
                                'truncated': len(content_text) > MAX_CONTENT_LENGTH
                            }
                        }
                        current_batch.append(record)
                        processed += 1
                        
                        # Procesar lote cuando alcanza el tamaño definido
                        if len(current_batch) >= BATCH_SIZE:
                            records.extend(current_batch)
                            logger.info(f"Procesadas {processed}/{total_pages} páginas de {book_name}")
                            current_batch = []
                            # Pausa entre lotes
                            time.sleep(PAUSE_BETWEEN_BATCHES)
                            
                    else:
                        logger.warning(f"Página {page_num} de {book_name} ignorada por contenido insuficiente")
                        
                except Exception as e:
                    logger.error(f"Error procesando página {page_num} de {book_name}: {str(e)}")
                    continue
            
            # Procesar último lote
            if current_batch:
                records.extend(current_batch)
            
            logger.info(f"Total de páginas procesadas de {book_name}: {len(records)}")
            return records
            
    except Exception as e:
        logger.error(f"Error procesando libro {file_path}: {str(e)}")
        return []

def main():
    """Función principal para procesar e indexar los libros de EGW."""
    conn = None
    cur = None
    try:
        # Verificar variables de entorno
        if not os.getenv('DATABASE_URL'):
            raise ValueError("DATABASE_URL no está configurada")
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY no está configurada")
            
        # Conectar a la base de datos
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Inicializar la base de datos
        init_database(cur)
        conn.commit()
        
        # Inicializar cliente de OpenAI
        client = OpenAI()
        
        # Procesar archivos JSON
        egw_folder = 'EGW BOOKS'
        json_files = [f for f in os.listdir(egw_folder) if f.endswith('.json')]
        logger.info(f"Encontrados {len(json_files)} libros para procesar")
        
        total_processed = 0
        total_errors = 0
        
        for json_file in json_files:
            try:
                logger.info(f"\nProcesando archivo: {json_file}")
                book_name = os.path.basename(json_file).replace('.json', '')
                
                # Inicializar progreso
                update_progress(cur, book_name, 0, 0, 'starting')
                
                # Procesar contenido del libro
                records = process_json_content(json_file)
                if not records:
                    logger.warning(f"No se encontraron registros válidos en {json_file}")
                    continue
                
                # Procesar en lotes para obtener embeddings
                current_batch = []
                processed_records = []
                
                for record in records:
                    current_batch.append(record)
                    
                    if len(current_batch) >= EMBEDDING_BATCH_SIZE:
                        batch_results = process_content_batch(current_batch, client)
                        processed_records.extend(batch_results)
                        current_batch = []
                        
                        # Actualizar progreso
                        update_progress(cur, book_name, len(records), len(processed_records))
                        
                        # Guardar lote en la base de datos
                        for record, embedding in batch_results:
                            try:
                                # Verificar si la página ya existe
                                cur.execute("""
                                    SELECT id FROM theological_content 
                                    WHERE source = %s AND (metadata->>'page')::int = %s
                                    LIMIT 1
                                """, (record['source'], record['metadata']['page']))
                                
                                if not cur.fetchone():
                                    cur.execute("""
                                        INSERT INTO theological_content 
                                        (title, content, source, metadata, embedding)
                                        VALUES (%s, %s, %s, %s, %s)
                                    """, (
                                        record['title'],
                                        record['content'],
                                        record['source'],
                                        Json(record['metadata']),
                                        embedding
                                    ))
                                else:
                                    logger.info(f"Página {record['metadata']['page']} de {record['source']} ya existe, omitiendo...")
                                
                                total_processed += 1
                                if total_processed % 10 == 0:
                                    logger.info(f"Procesados {total_processed} registros...")
                                    conn.commit()
                                    
                            except Exception as e:
                                total_errors += 1
                                logger.error(f"Error guardando registro: {str(e)}")
                                continue
                
                # Procesar último lote
                if current_batch:
                    batch_results = process_content_batch(current_batch, client)
                    processed_records.extend(batch_results)
                    
                    for record, embedding in batch_results:
                        try:
                            cur.execute("""
                                INSERT INTO theological_content 
                                (title, content, source, metadata, embedding)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (
                                record['title'],
                                record['content'],
                                record['source'],
                                Json(record['metadata']),
                                embedding
                            ))
                            
                            total_processed += 1
                            
                        except Exception as e:
                            total_errors += 1
                            logger.error(f"Error guardando registro: {str(e)}")
                            continue
                
                conn.commit()
                update_progress(cur, book_name, len(records), len(processed_records), 'completed')
                logger.info(f"Archivo {json_file} procesado exitosamente")
                
            except Exception as e:
                logger.error(f"Error procesando archivo {json_file}: {str(e)}")
                continue
        
        logger.info(f"\nProceso completado")
        logger.info(f"Total de registros procesados exitosamente: {total_processed}")
        logger.info(f"Total de errores encontrados: {total_errors}")
        
    except Exception as e:
        logger.error(f"Error durante la importación: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
