"""
Rutas revolucionarias de Nevin AI
Sistema unificado que integra Claude 4 + búsqueda web + validación doctrinal
"""

import logging
from flask import Blueprint, request, jsonify, render_template
from typing import Dict, Any

# Import the revolutionary Nevin AI core
from nevin_ai_core import get_nevin_core

logger = logging.getLogger(__name__)

# Create revolutionary Nevin blueprint
nevin_revolutionary = Blueprint('nevin_revolutionary', __name__, url_prefix='/api/nevin')

@nevin_revolutionary.route('/chat/revolutionary', methods=['POST'])
def revolutionary_chat():
    """
    Endpoint revolucionario que usa Claude 4 + búsqueda web + validación doctrinal
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No se recibieron datos"
            }), 400
        
        # Extract request parameters
        question = data.get('question', data.get('message', ''))
        context = data.get('context', '')
        language = data.get('language', 'Spanish')
        use_extended_thinking = data.get('extended_thinking', True)
        
        if not question:
            return jsonify({
                "success": False,
                "error": "Pregunta requerida"
            }), 400
        
        logger.info(f"Revolutionary Nevin query: {question[:100]}...")
        
        # Get the revolutionary Nevin AI core
        nevin_core = get_nevin_core()
        
        # Generate theological response with all revolutionary features
        result = nevin_core.generate_theological_response(
            question=question,
            context=context,
            language=language,
            use_extended_thinking=use_extended_thinking
        )
        
        if result.get('success'):
            logger.info(f"Revolutionary response generated successfully. EGW sources: {result.get('egw_sources', 0)}")
            
            return jsonify({
                "success": True,
                "response": result['response'],
                "metadata": {
                    "text_type": result.get('text_type'),
                    "egw_sources_found": result.get('egw_sources', 0),
                    "doctrinal_validation": result.get('doctrinal_validation', {}),
                    "thinking_tokens": result.get('thinking_tokens', 0),
                    "system_version": "Revolutionary Nevin AI v2.0",
                    "powered_by": "Claude 4 + EGW Web Search + Doctrinal Validation"
                }
            })
        else:
            logger.error(f"Revolutionary Nevin error: {result.get('error')}")
            return jsonify({
                "success": False,
                "error": result.get('error', 'Error desconocido')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in revolutionary chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@nevin_revolutionary.route('/search/egw', methods=['POST'])
def search_egw_writings():
    """
    Endpoint especializado para búsqueda de escritos de Ellen G. White
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 5)
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Query requerido"
            }), 400
        
        logger.info(f"EGW search query: {query}")
        
        # Get the revolutionary Nevin AI core
        nevin_core = get_nevin_core()
        
        # Search EGW writings
        results = nevin_core.search_egw_writings(query, max_results)
        
        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.content,
                "source": result.source,
                "book": result.egw_book,
                "chapter": result.chapter,
                "url": result.url,
                "relevance_score": result.relevance_score
            })
        
        return jsonify({
            "success": True,
            "results": formatted_results,
            "total_found": len(formatted_results),
            "query": query
        })
        
    except Exception as e:
        logger.error(f"Error in EGW search endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Error en búsqueda de EGW"
        }), 500

@nevin_revolutionary.route('/hermeneutics/analyze', methods=['POST'])
def analyze_hermeneutics():
    """
    Endpoint para análisis hermenéutico automático de textos bíblicos
    """
    try:
        data = request.get_json()
        biblical_text = data.get('text', '')
        reference = data.get('reference', '')
        
        if not biblical_text:
            return jsonify({
                "success": False,
                "error": "Texto bíblico requerido"
            }), 400
        
        # Get the revolutionary Nevin AI core
        nevin_core = get_nevin_core()
        
        # Identify text type
        text_type = nevin_core.identify_text_type(biblical_text, reference)
        
        # Create theological context
        from nevin_ai_core import TheologicalContext
        context = TheologicalContext(
            text_type=text_type,
            biblical_reference=reference
        )
        
        # Apply hermeneutic principles
        hermeneutic_analysis = nevin_core.apply_hermeneutic_principles(text_type, context)
        
        return jsonify({
            "success": True,
            "text_type": text_type.value,
            "hermeneutic_analysis": hermeneutic_analysis,
            "biblical_reference": reference
        })
        
    except Exception as e:
        logger.error(f"Error in hermeneutic analysis endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Error en análisis hermenéutico"
        }), 500

@nevin_revolutionary.route('/doctrine/validate', methods=['POST'])
def validate_doctrine():
    """
    Endpoint para validación doctrinal automática
    """
    try:
        data = request.get_json()
        content = data.get('content', '')
        category = data.get('category', 'general')
        
        if not content:
            return jsonify({
                "success": False,
                "error": "Contenido requerido"
            }), 400
        
        # Get the revolutionary Nevin AI core
        nevin_core = get_nevin_core()
        
        # Validate doctrinal content
        validation_result = nevin_core.validate_doctrinal_content(content, category)
        
        return jsonify({
            "success": True,
            "validation": validation_result
        })
        
    except Exception as e:
        logger.error(f"Error in doctrinal validation endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Error en validación doctrinal"
        }), 500

@nevin_revolutionary.route('/status', methods=['GET'])
def revolutionary_status():
    """
    Estado del sistema revolucionario de Nevin AI
    """
    try:
        # Get the revolutionary Nevin AI core
        nevin_core = get_nevin_core()
        
        return jsonify({
            "success": True,
            "system": "Revolutionary Nevin AI v2.0",
            "features": {
                "claude_4_integration": True,
                "egw_web_search": True,
                "hermeneutic_analysis": True,
                "doctrinal_validation": True,
                "extended_thinking": True
            },
            "hermeneutic_principles_loaded": bool(nevin_core.hermeneutic_principles),
            "doctrinal_validation_loaded": bool(nevin_core.doctrinal_validation),
            "status": "operational"
        })
        
    except Exception as e:
        logger.error(f"Error checking revolutionary status: {e}")
        return jsonify({
            "success": False,
            "error": "Error verificando estado del sistema"
        }), 500

# Register error handlers
@nevin_revolutionary.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado"
    }), 404

@nevin_revolutionary.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Error interno del servidor"
    }), 500