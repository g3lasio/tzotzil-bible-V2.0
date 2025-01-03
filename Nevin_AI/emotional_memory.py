
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class EmotionalMemory:
    def __init__(self):
        self.emotional_patterns = {}
        self.context_history = defaultdict(list)
        self.memory_retention = timedelta(days=7)
        
    def record_emotion(self, user_id: str, emotion: str, context: str):
        timestamp = datetime.now()
        if user_id not in self.emotional_patterns:
            self.emotional_patterns[user_id] = []
            
        self.emotional_patterns[user_id].append({
            'emotion': emotion,
            'context': context,
            'timestamp': timestamp.isoformat()
        })
        
        # Registrar contexto
        self.context_history[user_id].append({
            'content': context,
            'timestamp': timestamp,
            'emotion': emotion
        })
        
        # Limpiar memoria antigua
        self._cleanup_old_memories(user_id)
        
    def get_emotional_history(self, user_id: str) -> List[Dict]:
        return self.emotional_patterns.get(user_id, [])
        
    def get_recent_context(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Obtiene el contexto reciente de las conversaciones."""
        history = self.context_history.get(user_id, [])
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
    def analyze_emotional_trend(self, user_id: str) -> Dict:
        history = self.get_emotional_history(user_id)
        if not history:
            return {'trend': 'neutral', 'confidence': 0.0}
            
        recent_emotions = [entry['emotion'] for entry in history[-5:]]
        dominant = max(set(recent_emotions), key=recent_emotions.count)
        confidence = recent_emotions.count(dominant) / len(recent_emotions)
        
        return {
            'trend': dominant,
            'confidence': confidence,
            'context': self._get_emotional_context(user_id, dominant)
        }
        
    def _cleanup_old_memories(self, user_id: str):
        """Limpia memorias más antiguas que memory_retention."""
        cutoff = datetime.now() - self.memory_retention
        
        if user_id in self.context_history:
            self.context_history[user_id] = [
                mem for mem in self.context_history[user_id] 
                if datetime.fromisoformat(mem['timestamp']) > cutoff
            ]
            
    def _get_emotional_context(self, user_id: str, emotion: str) -> List[str]:
        """Recupera contextos relacionados con una emoción específica."""
        return [
            entry['content'] 
            for entry in self.context_history.get(user_id, [])
            if entry['emotion'] == emotion
        ]
