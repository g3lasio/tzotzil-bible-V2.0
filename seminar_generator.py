from datetime import datetime
from fpdf import FPDF
import textwrap
import os
from extensions import db
from models import BibleVerse
from knowledge_base_manager import KnowledgeBaseManager

class SeminarGenerator:
    def __init__(self):
        self.kb_manager = KnowledgeBaseManager()
        self.db = db.session

    def generate_seminar(self, topic, audience="general", duration="60min"):
        """Genera un seminario temático estructurado."""
        
        # Buscar contenido relevante usando el knowledge base
        content = self.kb_manager.search_knowledge_base(topic, top_k=5)
        
        seminar = {
            "title": self._generate_catchy_title(topic),
            "key_verse": self._find_relevant_verse(topic),
            "introduction": self._generate_introduction(topic, content),
            "sections": self._generate_sections(topic, content),
            "egw_quote": self._find_egw_quote(content),
            "reflection_questions": self._generate_questions(topic),
            "conclusion": self._generate_conclusion(topic, content)
        }
        
        return seminar

    def _generate_catchy_title(self, topic):
        """Genera un título cautivador basado en el tema."""
        titles = {
            "sanctuary": "🏛️ Desvelando los Misterios del Santuario Celestial",
            "second coming": "⚡ Señales Innegables del Pronto Regreso de Cristo",
            "sabbath": "🌅 El Regalo del Tiempo: Redescubriendo el Sábado",
            "prophecy": "📜 Profecías Apocalípticas: El Mapa Divino para el Tiempo del Fin"
        }
        return titles.get(topic.lower(), f"🔍 {topic.title()}: Una Perspectiva Bíblica Transformadora")

    def _find_relevant_verse(self, topic):
        """Busca un versículo clave relacionado con el tema."""
        verse = BibleVerse.query.filter(BibleVerse.text.like(f"%{topic}%")).first()
        return (verse.text, verse.reference) if verse else ("Daniel 12:3", "Los entendidos resplandecerán como el resplandor del firmamento")


    def _generate_introduction(self, topic, content):
        """Genera una introducción con una historia contemporánea."""
        # Aquí podrías tener un banco de historias o generarlas dinámicamente
        return {
            "story": "En 2023, un científico ateo quedó impactado al descubrir patrones matemáticos en las profecías bíblicas...",
            "objective": f"Este seminario explorará {topic} desde una perspectiva bíblica y práctica."
        }

    def _generate_sections(self, topic, content):
        """Genera las secciones principales del seminario."""
        return [
            {
                "title": "Fundamento Bíblico",
                "content": "Análisis detallado de las escrituras relacionadas..."
            },
            {
                "title": "Relevancia Actual",
                "content": "Aplicación práctica en el contexto moderno..."
            },
            {
                "title": "Llamado a la Acción",
                "content": "Pasos prácticos para implementar estas verdades..."
            }
        ]

    def _find_egw_quote(self, content):
        """Encuentra una cita relevante de Elena G. White."""
        if content:
            return {
                "text": content[0]['content'],
                "source": content[0]['metadata']['source']
            }
        return {
            "text": "La verdad presente debe ser nuestro tema principal...",
            "source": "Eventos de los Últimos Días"
        }

    def _generate_questions(self, topic):
        """Genera preguntas de reflexión."""
        return [
            "¿Cómo aplica esta verdad a tu vida diaria?",
            "¿Qué cambios específicos te invita Dios a realizar?",
            "¿Cómo compartirías esta verdad con otros?"
        ]

    def _generate_conclusion(self, topic, content):
        """Genera una conclusión impactante."""
        return {
            "summary": f"Las verdades sobre {topic} son fundamentales para nuestra fe...",
            "call_to_action": "Te invito a tomar una decisión hoy..."
        }

    def export_to_pdf(self, seminar, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seminar_{timestamp}.pdf"
    
    # Asegurar que el directorio existe
    output_dir = os.path.join('static', 'seminars')
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
        """Exporta el seminario a PDF con marca de agua."""
        try:
            from fpdf import FPDF
            pdf = FPDF()
        except ImportError:
            logging.error("FPDF no está instalado, no se puede generar PDF")
            return None
        pdf.add_page()
        
        # Configuración de fuentes
        pdf.set_font("Arial", "B", 24)
        
        # Marca de agua
        pdf.set_text_color(200, 200, 200)
        pdf.rotate(45, pdf.w/2, pdf.h/2)
        pdf.text(50, pdf.h/2, "Nevin AI - Seminario Adventista")
        pdf.rotate(0)
        pdf.set_text_color(0, 0, 0)
        
        # Título
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 20, seminar["title"], ln=True, align="C")
        
        # Versículo clave
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, f'"{seminar["key_verse"][1]}"', ln=True, align="C")
        pdf.cell(0, 10, f"- {seminar['key_verse'][0]}", ln=True, align="C")
        
        # Contenido
        self._add_section(pdf, "Introducción", seminar["introduction"]["story"])
        
        for section in seminar["sections"]:
            self._add_section(pdf, section["title"], section["content"])
        
        # Cita EGW
        pdf.add_page()
        self._add_section(pdf, "Inspiración", 
            f'"{seminar["egw_quote"]["text"]}"\n- {seminar["egw_quote"]["source"]}')
        
        # Preguntas
        self._add_section(pdf, "Reflexión", 
            "\n".join(f"• {q}" for q in seminar["reflection_questions"]))
        
        # Conclusión
        self._add_section(pdf, "Conclusión", 
            f"{seminar['conclusion']['summary']}\n\n{seminar['conclusion']['call_to_action']}")
        
        # Guardar PDF
        pdf.output(filename)

    def _add_section(self, pdf, title, content):
        """Añade una sección al PDF con formato."""
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Arial", "", 12)
        
        # Wrap text para mejor formato
        wrapped_text = textwrap.fill(content, width=80)
        pdf.multi_cell(0, 10, wrapped_text)
        pdf.ln(10)