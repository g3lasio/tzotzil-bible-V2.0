import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from openai import OpenAI, OpenAIError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI()  # This will automatically use OPENAI_API_KEY from environment

def detect_emotion(text: str) -> Dict[str, float]:
    """Detect emotions in the input text."""
    emotion_patterns = {
        'tristeza': ['triste', 'deprimido', 'solo', 'dolor', 'pena', 'angustia', 'desesperado'],
        'desmotivación': ['cansado', 'sin ganas', 'difícil', 'no puedo', 'rendirme', 'fracaso'],
        'búsqueda_motivación': ['ayuda', 'necesito fuerza', 'animo', 'esperanza', 'consejo'],
        'preocupación': ['preocupado', 'ansioso', 'miedo', 'inquieto', 'nervioso']
    }
    
    text_lower = text.lower()
    emotions = {}
    
    for emotion, keywords in emotion_patterns.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        emotions[emotion] = score / len(keywords) if score > 0 else 0.0
    
    return emotions

def get_ai_response(question: str, context: str = "", language: str = "Spanish", user_preferences: Dict = None) -> Dict[str, Any]:
    """Get AI response for the user's question."""
    try:
        user_preferences = user_preferences or {}
        
        # Detect emotions in current question
        emotions = detect_emotion(question)
        
        # Adjust prompt based on emotional context
        emotional_guidance = ""
        if any(score > 0.3 for score in emotions.values()):
            if emotions.get('tristeza', 0) > 0.3:
                emotional_guidance = "El usuario parece estar triste o afligido. Proporciona una respuesta compasiva y alentadora, usando versículos bíblicos de consuelo."
            elif emotions.get('desmotivación', 0) > 0.3:
                emotional_guidance = "El usuario parece estar desmotivado. Ofrece palabras de ánimo y versículos que hablen sobre la fortaleza en Dios."
            elif emotions.get('búsqueda_motivación', 0) > 0.3:
                emotional_guidance = "El usuario está buscando motivación. Comparte versículos inspiradores y mensajes de esperanza."
            elif emotions.get('preocupación', 0) > 0.3:
                emotional_guidance = "El usuario muestra preocupación. Ofrece versículos sobre la paz de Dios y Su cuidado."
        
        # Construct the prompt
        prompt = f'''
        Eres Nevin, un asistente virtual amigable y empático que ayuda a encontrar respuestas en la Biblia.
        
        Contexto emocional:
        {emotional_guidance}
        
        Formato de respuesta:
        1. Para versículos bíblicos:
           <div class="verse-box">
           [Texto del versículo]
           <small class="verse-ref">[Libro Capítulo:Versículo]</small>
           </div>

        2. Para citas de Elena G. White:
           <div class="quote-box">
           [Texto de la cita]
           <small class="quote-ref">[Nombre del Libro, página]</small>
           </div>

        3. Para información importante:
           <div class="info-box">
           [Información relevante]
           </div>

        4. Para listas:
           <ul class="bullet-list">
           <li>Punto 1</li>
           <li>Punto 2</li>
           </ul>

        Responde en {language} de manera profesional y estructurada.

        Conversación previa:
        {context}

        Mensaje del usuario: {question}
        '''
        
        logger.info("Sending request to OpenAI")
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres Nevin, un asistente virtual amigable y empático que ayuda a encontrar respuestas bíblicas y comparte pensamientos inspiradores de literatura cristiana como complemento."
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            
            if response.choices[0].message.content:
                response_text = response.choices[0].message.content.replace("\n", "<br>")
            
            # Generar PDF si es un seminario
            pdf_url = None
            if "Seminario generado" in response_text:
                try:
                    from seminar_generator import SeminarGenerator
                    generator = SeminarGenerator()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"seminar_{timestamp}.pdf"
                    output_dir = os.path.join('static', 'seminars')
                    os.makedirs(output_dir, exist_ok=True)
                    filepath = os.path.join(output_dir, filename)
                    
                    if generator.export_to_pdf({"content": response_text}, filepath):
                        pdf_url = f"/static/seminars/{filename}"
                        logger.info(f"PDF generado exitosamente: {filepath}")
                        response_text += f"\n\n[PDF_LINK]"  # Marcador para el frontend
                        return {
                            "success": True,
                            "response": response_text,
                            "pdf_url": pdf_url
                        }
                    
                    response_text += f"\n\nPuedes descargar este seminario en formato PDF aquí: {pdf_url}"
                    
                    return {
                        "success": True,
                        "response": response_text,
                        "pdf_url": pdf_url
                    }
                except Exception as e:
                    logger.error(f"Error generando PDF: {str(e)}")

            # Retornar la respuesta y detener el procesamiento
            return {
                "success": True,
                "response": response_text,
                "pdf_url": pdf_url
            }
            
        except OpenAIError as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            return {
                "success": False,
                "error": "Lo siento, hubo un error al procesar tu pregunta con OpenAI. Por favor, intenta nuevamente."
            }
            
    except Exception as e:
        logger.error(f"Error in get_ai_response: {str(e)}")
        return {
            "success": False,
            "error": "Lo siento, hubo un error inesperado. Por favor, intenta nuevamente."
        }
    
    # Asegurar que no haya procesamiento adicional después del return