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
openai_client = OpenAI()

def format_bible_verse(verse_text: str, reference: str) -> str:
    """Format a Bible verse with proper HTML structure."""
    return f'''
    <div class="verse-box">
        {verse_text}
        <small class="verse-ref">{reference}</small>
    </div>
    '''

def format_egw_quote(quote_text: str, source: str) -> str:
    """Format an Ellen G. White quote with proper HTML structure."""
    return f'''
    <div class="quote-box">
        {quote_text}
        <small class="quote-ref">{source}</small>
    </div>
    '''

def format_info_section(text: str) -> str:
    """Format informational content with proper HTML structure."""
    return f'<div class="info-box">{text}</div>'

def format_bullet_list(items: List[str]) -> str:
    """Format a list of items with proper HTML structure."""
    list_items = "".join([f"<li>{item}</li>" for item in items])
    return f'<ul class="bullet-list">{list_items}</ul>'

def detect_emotion(text: str) -> Dict[str, float]:
    """Detect emotions in the input text with expanded emotional patterns."""
    emotion_patterns = {
        'tristeza': ['triste', 'deprimido', 'solo', 'dolor', 'pena', 'angustia', 'desesperado', 'sufrimiento'],
        'desmotivación': ['cansado', 'sin ganas', 'difícil', 'no puedo', 'rendirme', 'fracaso', 'desánimo'],
        'búsqueda_motivación': ['ayuda', 'necesito fuerza', 'animo', 'esperanza', 'consejo', 'guía'],
        'preocupación': ['preocupado', 'ansioso', 'miedo', 'inquieto', 'nervioso', 'incertidumbre'],
        'gratitud': ['gracias', 'agradecido', 'bendecido', 'favor', 'reconocimiento'],
        'alegría': ['feliz', 'gozo', 'contento', 'paz', 'satisfecho', 'regocijo']
    }

    text_lower = text.lower()
    emotions = {}

    for emotion, keywords in emotion_patterns.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        emotions[emotion] = score / len(keywords) if score > 0 else 0.0

    return emotions

def get_emotional_response_template(emotions: Dict[str, float]) -> str:
    """Get appropriate response template based on emotional context."""
    highest_emotion = max(emotions.items(), key=lambda x: x[1]) if emotions else ('neutral', 0)

    templates = {
        'tristeza': "Comprendo que estés pasando por un momento difícil. La Biblia nos ofrece consuelo y esperanza:",
        'desmotivación': "A veces el camino parece difícil, pero Dios nos da fuerzas renovadas:",
        'búsqueda_motivación': "Me alegra que busques orientación. La palabra de Dios es nuestra mejor guía:",
        'preocupación': "Dios conoce tus preocupaciones y nos dice en su palabra:",
        'gratitud': "Es hermoso ver tu corazón agradecido. Como dice la Escritura:",
        'alegría': "Tu gozo refleja la bendición de Dios. Como está escrito:",
        'neutral': "La palabra de Dios nos enseña:"
    }

    return templates.get(highest_emotion[0], templates['neutral'])

def get_ai_response(question: str, context: str = "", language: str = "Spanish", user_preferences: Dict = None, user_id: str = None) -> Dict[str, Any]:
    """Get AI response with improved formatting and emotional intelligence."""
    try:
        user_preferences = user_preferences or {}

        # Detect emotions in current question
        emotions = detect_emotion(question)
        emotional_template = get_emotional_response_template(emotions)

        # Adjust prompt based on emotional context
        emotional_guidance = ""
        if any(score > 0.3 for score in emotions.values()):
            highest_emotion = max(emotions.items(), key=lambda x: x[1])
            emotional_map = {
                'tristeza': "El usuario muestra tristeza. Ofrece consuelo con versículos específicos y palabras de esperanza.",
                'desmotivación': "El usuario está desmotivado. Comparte testimonios bíblicos de superación y promesas de fortaleza.",
                'búsqueda_motivación': "El usuario busca dirección. Proporciona versículos inspiradores y consejos prácticos.",
                'preocupación': "El usuario está preocupado. Comparte versículos sobre la paz de Dios y Su cuidado providencial.",
                'gratitud': "El usuario muestra gratitud. Refuerza esta actitud con versículos sobre el agradecimiento.",
                'alegría': "El usuario expresa gozo. Complementa con versículos sobre el regocijo en el Señor."
            }
            emotional_guidance = emotional_map.get(highest_emotion[0], "")

        # Construct the enhanced prompt
        prompt = f'''
        Eres Nevin, un asistente pastoral y bíblico cálido y sabio que valora la concisión. 
        Tu propósito es ayudar a las personas a comprender mejor la Biblia y conectar emocionalmente con ellas.

        PERSONALIDAD:
        - Muestra empatía genuina y comprensión
        - Usa un tono conversacional y amigable
        - Incluye toques de humor apropiado cuando sea oportuno
        - Mantén un balance entre profundidad espiritual y accesibilidad

        ESTRUCTURA DE RESPUESTAS:
        1. Conexión emocional inicial
        2. Respuesta basada en sabiduría bíblica
        3. Referencias relevantes (bíblicas y de Elena G. White)
        4. Aplicación práctica y personal
        5. Invitación al diálogo continuo

        FORMATO HTML:
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

        Contexto emocional detectado:
        {emotional_guidance}

        Tono sugerido para la respuesta:
        {emotional_template}

        Conversación previa:
        {context}

        Responde en {language} de manera estructurada y empática.

        Pregunta del usuario: {question}
        '''

        logger.info("Sending request to OpenAI with enhanced prompt structure")
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres Nevin, un asistente pastoral y bíblico cálido y sabio que valora la concisión y la precisión en las citas bíblicas y de Elena G. White."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                presence_penalty=0.6,
                frequency_penalty=0.1
            )

            response_text = response.choices[0].message.content

            # Log successful response generation
            logger.info("Successfully generated AI response")

            return {
                "success": True,
                "response": response_text
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