
import os
import logging
from datetime import datetime
from fpdf import FPDF
from replit.object_storage import Client

class SeminarGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.storage_client = Client()
        
    def generate_seminar(self, topic, audience, duration):
        # Lógica existente de generación...
        return {
            'title': f'Seminario: {topic}',
            'audience': audience,
            'duration': duration,
            'content': 'Contenido del seminario...'
        }
        
    def export_to_pdf(self, seminar_data, filename):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, seminar_data['title'], ln=True)
            
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f"Audiencia: {seminar_data['audience']}", ln=True)
            pdf.cell(0, 10, f"Duración: {seminar_data['duration']}", ln=True)
            pdf.multi_cell(0, 10, seminar_data['content'])
            
            # Guardar PDF en memoria
            pdf_content = pdf.output(dest='S').encode('latin-1')
            
            # Subir al Object Storage
            self.storage_client.upload_bytes(filename, pdf_content)
            
            # Generar URL temporal válida por 1 hora
            download_url = self.storage_client.get_download_url(filename, expire_in=3600)
            
            return True, download_url
            
        except Exception as e:
            self.logger.error(f"Error generando PDF: {str(e)}")
            return False, None
