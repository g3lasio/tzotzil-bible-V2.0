
import json
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
from collections import defaultdict

class EnhancedMemory:
    def __init__(self):
        self.emotional_patterns = {}
        self.conversation_history = defaultdict(list)
        self.behavioral_patterns = defaultdict(dict)
        self.topic_interests = defaultdict(lambda: defaultdict(int))
        self.learning_style = defaultdict(dict)
        self.scientific_queries = defaultdict(list)
        
    def record_interaction(self, user_id: str, interaction: Dict):
        timestamp = datetime.now().isoformat()
        
        # Registrar emoción y contexto
        if 'emotion' in interaction:
            self.record_emotion(user_id, interaction['emotion'], interaction.get('context', ''))
            
        # Registrar conversación
        self.conversation_history[user_id].append({
            'timestamp': timestamp,
            'content': interaction.get('content', ''),
            'type': interaction.get('type', 'general'),
            'topic': interaction.get('topic', 'general'),
            'response': interaction.get('response', ''),
        })
        
        # Analizar intereses y patrones
        self._analyze_topic_interest(user_id, interaction)
        self._analyze_learning_style(user_id, interaction)
        
        # Registrar consultas científicas
        if interaction.get('type') == 'scientific':
            self.scientific_queries[user_id].append({
                'timestamp': timestamp,
                'query': interaction.get('content', ''),
                'field': interaction.get('field', 'general')
            })
    
    def record_emotion(self, user_id: str, emotion: str, context: str):
        if user_id not in self.emotional_patterns:
            self.emotional_patterns[user_id] = []
            
        self.emotional_patterns[user_id].append({
            'emotion': emotion,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Obtiene un perfil completo del usuario basado en todas las interacciones."""
        recent_emotions = self.get_recent_emotions(user_id, limit=5)
        topics = self.get_top_topics(user_id)
        learning_style = self.get_learning_style(user_id)
        scientific_interests = self.get_scientific_interests(user_id)
        
        return {
            'emotional_trend': self.analyze_emotional_trend(user_id),
            'recent_emotions': recent_emotions,
            'top_topics': topics,
            'learning_style': learning_style,
            'scientific_interests': scientific_interests,
            'interaction_patterns': self._get_interaction_patterns(user_id)
        }
    
    def get_relevant_context(self, user_id: str, current_topic: str) -> List[Dict]:
        """Obtiene contexto relevante para la conversación actual."""
        history = self.conversation_history[user_id]
        return [
            h for h in history[-10:]
            if self._is_relevant_to_topic(h['topic'], current_topic)
        ]
    
    def get_scientific_interests(self, user_id: str) -> Dict:
        """Analiza los intereses científicos del usuario."""
        queries = self.scientific_queries[user_id]
        fields = defaultdict(int)
        
        for query in queries:
            fields[query['field']] += 1
            
        return dict(fields)
    
    def _analyze_topic_interest(self, user_id: str, interaction: Dict):
        topic = interaction.get('topic', 'general')
        self.topic_interests[user_id][topic] += 1
    
    def _analyze_learning_style(self, user_id: str, interaction: Dict):
        style_indicators = {
            'asks_for_examples': ['ejemplo', 'ilustra', 'muestra'],
            'prefers_technical': ['técnico', 'específico', 'detallado'],
            'visual_learner': ['imagen', 'gráfico', 'visual'],
            'practical_application': ['aplicar', 'práctica', 'usar']
        }
        
        content = interaction.get('content', '').lower()
        for style, indicators in style_indicators.items():
            if any(indicator in content for indicator in indicators):
                self.learning_style[user_id][style] = self.learning_style[user_id].get(style, 0) + 1
    
    def _is_relevant_to_topic(self, history_topic: str, current_topic: str) -> bool:
        """Determina si un tema histórico es relevante para el tema actual."""
        # Implementar lógica de relevancia más sofisticada aquí
        return history_topic == current_topic or history_topic == 'general'
    
    def _get_interaction_patterns(self, user_id: str) -> Dict:
        """Analiza patrones de interacción del usuario."""
        history = self.conversation_history[user_id]
        
        time_patterns = self._analyze_time_patterns([h['timestamp'] for h in history])
        topic_sequences = self._analyze_topic_sequences([h['topic'] for h in history])
        
        return {
            'preferred_times': time_patterns,
            'topic_sequences': topic_sequences,
            'average_interaction_length': np.mean([len(h['content']) for h in history]) if history else 0
        }
    
    def _analyze_time_patterns(self, timestamps: List[str]) -> Dict:
        """Analiza patrones temporales de interacción."""
        hours = [datetime.fromisoformat(ts).hour for ts in timestamps]
        return {
            'peak_hour': max(set(hours), key=hours.count) if hours else None,
            'active_periods': self._get_active_periods(hours)
        }
    
    def _analyze_topic_sequences(self, topics: List[str]) -> List[tuple]:
        """Analiza secuencias comunes de temas."""
        sequences = []
        for i in range(len(topics) - 1):
            sequences.append((topics[i], topics[i + 1]))
        return sequences
    
    def _get_active_periods(self, hours: List[int]) -> List[str]:
        """Identifica períodos activos del día."""
        periods = {
            'morning': (5, 11),
            'afternoon': (12, 17),
            'evening': (18, 22),
            'night': (23, 4)
        }
        
        active = []
        for period, (start, end) in periods.items():
            if any(start <= h <= end for h in hours):
                active.append(period)
        
        return active
