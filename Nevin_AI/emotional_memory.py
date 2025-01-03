
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from collections import defaultdict
from textblob import TextBlob

class EnhancedMemory:
    def __init__(self):
        self.emotional_patterns = {}
        self.conversation_history = defaultdict(list)
        self.behavioral_patterns = defaultdict(dict)
        self.topic_interests = defaultdict(lambda: defaultdict(int))
        self.learning_style = defaultdict(dict)
        self.personality_traits = defaultdict(dict)
        self.interaction_metadata = defaultdict(list)
        self.belief_patterns = defaultdict(dict)
        self.emotional_triggers = defaultdict(list)
        self.user_knowledge_level = defaultdict(dict)
        self.memory_retention = 500  # Aumentar retención de memoria

    def record_interaction(self, user_id: str, interaction: Dict):
        timestamp = datetime.now().isoformat()
        
        # Análisis de sentimientos detallado
        content = interaction.get('content', '')
        sentiment = self._analyze_sentiment(content)
        
        # Metadata enriquecida
        metadata = {
            'timestamp': timestamp,
            'content': content,
            'type': interaction.get('type', 'general'),
            'topic': interaction.get('topic', 'general'),
            'sentiment': sentiment,
            'word_count': len(content.split()),
            'question_type': self._identify_question_type(content),
            'complexity_level': self._analyze_complexity(content),
            'doctrinal_references': self._extract_doctrinal_references(content),
            'user_state': interaction.get('user_state', {})
        }
        
        # Registro de patrones
        self._update_behavioral_patterns(user_id, metadata)
        self._update_belief_patterns(user_id, content)
        self._update_knowledge_level(user_id, metadata)
        self._record_emotional_triggers(user_id, content, sentiment)
        
        # Mantener historial con límite aumentado
        self.conversation_history[user_id].append(metadata)
        if len(self.conversation_history[user_id]) > self.memory_retention:
            self.conversation_history[user_id].pop(0)

    def _analyze_sentiment(self, text: str) -> Dict:
        analysis = TextBlob(text)
        return {
            'polarity': analysis.sentiment.polarity,
            'subjectivity': analysis.sentiment.subjectivity,
            'emotional_state': self._classify_emotional_state(analysis.sentiment.polarity)
        }

    def _identify_question_type(self, text: str) -> str:
        question_types = {
            'doctrinal': ['doctrina', 'creencia', 'enseña'],
            'personal': ['siento', 'pienso', 'creo'],
            'theological': ['biblia', 'escritura', 'profecía'],
            'practical': ['cómo', 'qué debo', 'aplicar']
        }
        
        text_lower = text.lower()
        for qtype, keywords in question_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return qtype
        return 'general'

    def _analyze_complexity(self, text: str) -> str:
        words = len(text.split())
        theological_terms = ['exégesis', 'hermenéutica', 'soteriología', 'escatología']
        term_count = sum(1 for term in theological_terms if term.lower() in text.lower())
        
        if words > 50 or term_count > 2:
            return 'advanced'
        elif words > 20 or term_count > 0:
            return 'intermediate'
        return 'basic'

    def get_user_profile(self, user_id: str) -> Dict:
        """Obtiene un perfil detallado del usuario basado en todas las interacciones."""
        profile = {
            'emotional_trends': self._analyze_emotional_trends(user_id),
            'knowledge_level': self.user_knowledge_level[user_id],
            'topic_interests': self._get_weighted_interests(user_id),
            'behavioral_patterns': self._analyze_behavioral_patterns(user_id),
            'interaction_style': self._analyze_interaction_style(user_id),
            'belief_system': self._analyze_belief_patterns(user_id),
            'learning_preferences': self._analyze_learning_preferences(user_id),
            'emotional_triggers': self._get_emotional_triggers(user_id),
            'engagement_level': self._calculate_engagement_level(user_id),
            'doctrinal_understanding': self._assess_doctrinal_understanding(user_id)
        }
        return profile

    def _analyze_emotional_trends(self, user_id: str) -> Dict:
        if not self.conversation_history[user_id]:
            return {}
            
        recent_emotions = [
            interaction['sentiment']['emotional_state']
            for interaction in self.conversation_history[user_id][-20:]
        ]
        
        return {
            'dominant_emotion': max(set(recent_emotions), key=recent_emotions.count),
            'emotional_stability': self._calculate_emotional_stability(recent_emotions),
            'trend': self._identify_emotional_trend(recent_emotions)
        }

    def _calculate_engagement_level(self, user_id: str) -> str:
        interactions = self.conversation_history[user_id]
        if not interactions:
            return "unknown"
            
        last_week = datetime.now() - timedelta(days=7)
        recent_interactions = [
            i for i in interactions
            if datetime.fromisoformat(i['timestamp']) > last_week
        ]
        
        engagement_score = len(recent_interactions) * 0.3
        engagement_score += sum(len(i['content']) for i in recent_interactions) * 0.01
        
        if engagement_score > 50:
            return "high"
        elif engagement_score > 20:
            return "medium"
        return "low"

    def _assess_doctrinal_understanding(self, user_id: str) -> Dict:
        doctrinal_topics = defaultdict(int)
        topic_complexity = defaultdict(list)
        
        for interaction in self.conversation_history[user_id]:
            if 'doctrinal_references' in interaction:
                for topic in interaction['doctrinal_references']:
                    doctrinal_topics[topic] += 1
                    topic_complexity[topic].append(interaction['complexity_level'])
        
        return {
            'topics_engaged': dict(doctrinal_topics),
            'understanding_level': {
                topic: max(set(levels), key=levels.count)
                for topic, levels in topic_complexity.items()
            }
        }

    def get_relevant_context(self, user_id: str, current_topic: str) -> List[Dict]:
        """Obtiene contexto relevante enriquecido para la conversación actual."""
        relevant_interactions = []
        for interaction in self.conversation_history[user_id][-self.memory_retention:]:
            relevance_score = self._calculate_relevance(interaction, current_topic)
            if relevance_score > 0.5:
                interaction['relevance_score'] = relevance_score
                relevant_interactions.append(interaction)
        
        return sorted(relevant_interactions, key=lambda x: x['relevance_score'], reverse=True)

    def _calculate_relevance(self, interaction: Dict, current_topic: str) -> float:
        base_score = 0.0
        
        # Relevancia por tema
        if interaction['topic'] == current_topic:
            base_score += 0.6
        
        # Relevancia temporal (más reciente = más relevante)
        time_diff = datetime.now() - datetime.fromisoformat(interaction['timestamp'])
        time_score = 1.0 / (1.0 + time_diff.total_seconds() / 86400)  # Decaimiento diario
        
        # Relevancia por complejidad
        complexity_match = self._complexity_relevance(interaction['complexity_level'])
        
        return min(1.0, base_score + (time_score * 0.2) + (complexity_match * 0.2))

    def _classify_emotional_state(self, polarity: float) -> str:
        if polarity > 0.5:
            return 'very_positive'
        elif polarity > 0:
            return 'positive'
        elif polarity < -0.5:
            return 'very_negative'
        elif polarity < 0:
            return 'negative'
        return 'neutral'
