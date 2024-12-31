
import os
import logging
from datetime import datetime
from fpdf import FPDF

class SeminarGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _add_section(self, pdf, title, content):
        """Añade una sección al PDF con formato."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, content)

    def export_to_pdf(self, seminar, filepath):
        """Exporta el seminario a PDF optimizado para dispositivos móviles."""
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Configurar PDF para mejor visualización en móviles
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_margin(10)
            
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 20, seminar.get("title", "Seminario"), ln=True, align="C")
            
            # Contenido
            pdf.set_font("Arial", "", 12)
            for section in seminar.get("sections", []):
                self._add_section(pdf, section.get("title", ""), section.get("content", ""))
                
            # Conclusión
            if "conclusion" in seminar:
                self._add_section(pdf, "Conclusión", seminar["conclusion"])
                
            # Guardar PDF
            pdf.output(filepath)
            self.logger.info(f"PDF generado exitosamente: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generando PDF: {str(e)}")
            return False
