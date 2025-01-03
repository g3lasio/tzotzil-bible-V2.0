
import os
import logging
from datetime import datetime
from fpdf import FPDF
from typing import Dict, Tuple, Optional

class PDFGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_pdf(self, content: str, title: str = "Respuesta de Nevin") -> Tuple[bool, Optional[str]]:
        try:
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Agregar título
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt=title, ln=1, align='C')
            pdf.ln(10)
            
            # Agregar contenido
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=content)
            
            # Generar nombre único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nevin_respuesta_{timestamp}.pdf"
            filepath = os.path.join("static", "seminars", filename)
            
            # Crear directorio si no existe
            os.makedirs(os.path.join("static", "seminars"), exist_ok=True)
            
            # Guardar PDF
            pdf.output(filepath)
            
            return True, f"/static/seminars/{filename}"
            
        except Exception as e:
            self.logger.error(f"Error generando PDF: {str(e)}")
            return False, None
