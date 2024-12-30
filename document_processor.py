
import json
import logging
try:
    import fitz  # PyMuPDF para PDFs
except ImportError:
    import logging
    logging.warning("PyMuPDF no disponible, algunas funciones de PDF estarán limitadas")
    fitz = None
from pathlib import Path
from typing import Generator, Dict, Any, List, Union
from database import get_db

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = logging.getLogger(__name__)
        self.db = get_db()

    def process_jsonl(self, file_path: str) -> List[Dict[str, Any]]:
        """Procesa archivo JSON de EGW."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                book_name = Path(file_path).stem
                documents = []
                
                for page in data:
                    if not self._is_valid_page(page):
                        continue
                        
                    content = self._extract_content(page)
                    if len(content) < 50:
                        continue
                        
                    chunks = self._chunk_text(content)
                    for i, chunk in enumerate(chunks):
                        doc = {
                            'title': f"{book_name} - Página {page.get('page', 0)}",
                            'content': chunk,
                            'metadata': {
                                'source': book_name,
                                'page': page.get('page', 0),
                                'type': 'egw',
                                'chunk': i
                            }
                        }
                        documents.append(doc)
                        
                return documents
                
        except Exception as e:
            self.logger.error(f"Error procesando {file_path}: {str(e)}")
            return []

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Procesa archivo PDF y extrae contenido en chunks."""
        try:
            documents = []
            book_name = Path(pdf_path).stem
            
            with fitz.open(pdf_path) as doc:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    content = page.get_text()
                    
                    if len(content) < 50:
                        continue
                        
                    chunks = self._chunk_text(content)
                    for i, chunk in enumerate(chunks):
                        doc_entry = {
                            'title': f"{book_name} - Página {page_num + 1}",
                            'content': chunk,
                            'metadata': {
                                'source': book_name,
                                'page': page_num + 1,
                                'type': 'theological',
                                'chunk': i
                            }
                        }
                        documents.append(doc_entry)
                        
            return documents
            
        except Exception as e:
            self.logger.error(f"Error procesando PDF {pdf_path}: {e}")
            return []

    def _is_valid_page(self, page: Dict) -> bool:
        """Valida estructura básica de página."""
        return isinstance(page, dict) and 'content' in page

    def _extract_content(self, page: Dict) -> str:
        """Extrae y limpia contenido de página."""
        content = page.get('content', [])
        if isinstance(content, list):
            return ' '.join(str(item) for item in content if item)
        return str(content)

    def _chunk_text(self, text: str) -> List[str]:
        """Divide texto en chunks con overlap."""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            
            if end >= text_len:
                chunk = text[start:text_len]
            else:
                while end > start and text[end] != ' ':
                    end -= 1
                chunk = text[start:end]
            
            if len(chunk) >= 100:
                chunks.append(chunk)
            
            start = end - self.overlap
            
        return chunks

