
import os
import logging
from datetime import datetime
from fpdf import FPDF
from replit.object_storage import Client

class SeminarGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.storage_client = Client()

    def _add_section(self, pdf, title, content):
        """Añade una sección al PDF con formato."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, content)

    def export_to_pdf(self, seminar, filename):
        """Exporta el seminario a PDF y lo sube al Object Storage."""
        try:
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_margins(10, 10, 10)
            
            # Título
            pdf.add_page()
            pdf.set_font("Arial", "B", 24)
            pdf.cell(0, 20, seminar.get("title", "Seminario"), ln=True, align="C")
            
            # Contenido
            for section in seminar.get("sections", []):
                self._add_section(pdf, section.get("title", ""), section.get("content", ""))
                
            if "conclusion" in seminar:
                self._add_section(pdf, "Conclusión", seminar["conclusion"])
            
            # Guardar PDF en memoria
            pdf_content = pdf.output(dest='S').encode('latin-1')
            
            # Subir al Object Storage
            storage_path = f"seminars/{filename}"
            self.storage_client.upload_bytes(storage_path, pdf_content)
            
            # Generar URL firmada para descarga
            signed_url = self.storage_client.get_signed_url(storage_path, expiry=3600)  # 1 hora
            
            self.logger.info(f"PDF generado y subido exitosamente: {storage_path}")
            return True, signed_url
            
        except Exception as e:
            self.logger.error(f"Error generando PDF: {str(e)}")
            return False, None
