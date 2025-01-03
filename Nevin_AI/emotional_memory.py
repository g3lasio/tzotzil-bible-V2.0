
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class EmotionalMemory:
    def __init__(self):
        self.emotional_patterns = {}
        self.context_history = defaultdict(list)
        self.memory_retention = timedelta(days=30)  # Aumentado de 7 a 30 días
        self.interaction_patterns = defaultdict(dict)
        self.topic_interests = defaultdict(lambda: defaultdict(float))
        self.vectorizer = TfidfVectorizer()
        self.user_vectors = {}
        
    def record_emotion(self, user_id: str, emotion: str, context: str, interaction_type: str = "general"):
        timestamp = datetime.now()
        
        # Registro emocional mejorado
        if user_id not in self.emotional_patterns:
            self.emotional_patterns[user_id] = []
            
        emotional_data = {
            'emotion': emotion,
            'context': context,
            'timestamp': timestamp.isoformat(),
            'interaction_type': interaction_type,
            'intensity': self._calculate_emotional_intensity(context),
        }
        
        self.emotional_patterns[user_id].append(emotional_data)
        
        # Análisis contextual profundo
        self._update_context_vectors(user_id, context)
        self._analyze_interaction_patterns(user_id, context, emotion)
        self._update_topic_interests(user_id, context)
        
        # Limpieza automática
        self._cleanup_old_memories(user_id)
        
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calcula la intensidad emocional del texto."""
        emotional_keywords = {
            'high': ['muy', 'extremadamente', 'absolutamente', 'profundamente'],
            'medium': ['bastante', 'considerablemente', 'significativamente'],
            'low': ['poco', 'ligeramente', 'algo']
        }
        
        text_lower = text.lower()
        intensity = 0.5  # valor base
        
        for level, keywords in emotional_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                intensity = 0.9 if level == 'high' else 0.5 if level == 'medium' else 0.2
                break
                
        return intensity
        
    def _update_context_vectors(self, user_id: str, context: str):
        """Actualiza los vectores de contexto del usuario."""
        if not context.strip():
            return
            
        if user_id not in self.user_vectors:
            self.user_vectors[user_id] = []
            
        self.user_vectors[user_id].append(context)
        
        # Actualizar el vector TF-IDF
        if len(self.user_vectors[user_id]) > 1:
            try:
                vectors = self.vectorizer.fit_transform(self.user_vectors[user_id])
                self.user_vectors[user_id] = vectors.toarray()[-1]
            except Exception:
                pass
                
    def _analyze_interaction_patterns(self, user_id: str, context: str, emotion: str):
        """Analiza patrones de interacción del usuario."""
        if user_id not in self.interaction_patterns:
            self.interaction_patterns[user_id] = {
                'topics': defaultdict(int),
                'emotional_transitions': [],
                'conversation_style': defaultdict(int),
                'learning_preferences': defaultdict(int)
            }
            
        # Análisis de temas
        topics = self._extract_topics(context)
        for topic in topics:
            self.interaction_patterns[user_id]['topics'][topic] += 1
            
        # Registrar transición emocional
        if self.emotional_patterns[user_id]:
            last_emotion = self.emotional_patterns[user_id][-1]['emotion']
            self.interaction_patterns[user_id]['emotional_transitions'].append(
                (last_emotion, emotion)
            )
            
    def _extract_topics(self, text: str) -> List[str]:
        """Extrae temas principales del texto."""
        # Implementar lógica de extracción de temas
        topics = []
        biblical_keywords = ['biblia', 'dios', 'jesús', 'oración', 'fe']
        doctrinal_keywords = ['doctrina', 'profecía', 'santuario', 'sábado']
        
        text_lower = text.lower()
        
        for keyword in biblical_keywords + doctrinal_keywords:
            if keyword in text_lower:
                topics.append(keyword)
                
        return list(set(topics))
        
    def _update_topic_interests(self, user_id: str, context: str):
        """Actualiza los intereses temáticos del usuario."""
        topics = self._extract_topics(context)
        for topic in topics:
            self.topic_interests[user_id][topic] += 1
            
    def get_user_profile(self, user_id: str) -> Dict:
        """Obtiene un perfil completo del usuario."""
        if user_id not in self.emotional_patterns:
            return {}
            
        recent_history = self.get_emotional_history(user_id)
        emotional_trend = self.analyze_emotional_trend(user_id)
        
        topics_of_interest = sorted(
            self.topic_interests[user_id].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'emotional_trend': emotional_trend,
            'topics_of_interest': topics_of_interest[:5],
            'interaction_style': self._analyze_interaction_style(user_id),
            'learning_preferences': self._detect_learning_preferences(user_id),
            'context_awareness': self._generate_context_awareness(user_id)
        }
        
    def _analyze_interaction_style(self, user_id: str) -> str:
        """Analiza el estilo de interacción del usuario."""
        if user_id not in self.interaction_patterns:
            return "neutral"
            
        patterns = self.interaction_patterns[user_id]
        emotional_transitions = patterns.get('emotional_transitions', [])
        
        if not emotional_transitions:
            return "neutral"
            
        # Análisis de patrones emocionales
        transitions_count = len(emotional_transitions)
        emotional_stability = len(set(t[0] for t in emotional_transitions)) / transitions_count
        
        if emotional_stability < 0.3:
            return "estable"
        elif emotional_stability < 0.6:
            return "variable"
        else:
            return "dinámico"
            
    def _detect_learning_preferences(self, user_id: str) -> List[str]:
        """Detecta preferencias de aprendizaje del usuario."""
        preferences = []
        if user_id in self.interaction_patterns:
            patterns = self.interaction_patterns[user_id]
            
            # Análisis de patrones de aprendizaje
            if patterns['topics'].get('biblia', 0) > patterns['topics'].get('doctrina', 0):
                preferences.append("orientado_a_escrituras")
            else:
                preferences.append("orientado_a_doctrina")
                
            # Más análisis de preferencias...
            
        return preferences
        
    def _generate_context_awareness(self, user_id: str) -> Dict:
        """Genera consciencia contextual para el usuario."""
        return {
            'recent_topics': self._get_recent_topics(user_id),
            'emotional_patterns': self._get_emotional_patterns(user_id),
            'interaction_depth': self._calculate_interaction_depth(user_id)
        }
        
    def _get_recent_topics(self, user_id: str) -> List[str]:
        """Obtiene los temas recientes del usuario."""
        if user_id not in self.interaction_patterns:
            return []
            
        topics = self.interaction_patterns[user_id]['topics']
        return sorted(topics.keys(), key=topics.get, reverse=True)[:5]
        
    def _get_emotional_patterns(self, user_id: str) -> Dict:
        """Obtiene patrones emocionales del usuario."""
        if user_id not in self.emotional_patterns:
            return {}
            
        emotions = [entry['emotion'] for entry in self.emotional_patterns[user_id]]
        return dict(Counter(emotions))
        
    def _calculate_interaction_depth(self, user_id: str) -> float:
        """Calcula la profundidad de interacción del usuario."""
        if user_id not in self.context_history:
            return 0.0
            
        contexts = self.context_history[user_id]
        if not contexts:
            return 0.0
            
        # Análisis de profundidad basado en longitud y complejidad
        avg_length = sum(len(c['content'].split()) for c in contexts) / len(contexts)
        return min(1.0, avg_length / 100)  # Normalizado a 1.0
