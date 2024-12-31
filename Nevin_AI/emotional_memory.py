
import json
from datetime import datetime
from typing import Dict, List

class EmotionalMemory:
    def __init__(self):
        self.emotional_patterns = {}
        
    def record_emotion(self, user_id: str, emotion: str, context: str):
        if user_id not in self.emotional_patterns:
            self.emotional_patterns[user_id] = []
            
        self.emotional_patterns[user_id].append({
            'emotion': emotion,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_emotional_history(self, user_id: str) -> List[Dict]:
        return self.emotional_patterns.get(user_id, [])
        
    def analyze_emotional_trend(self, user_id: str) -> Dict:
        history = self.get_emotional_history(user_id)
        if not history:
            return {'trend': 'neutral'}
            
        emotions = [entry['emotion'] for entry in history[-5:]]
        dominant = max(set(emotions), key=emotions.count)
        return {
            'trend': dominant,
            'consistency': emotions.count(dominant) / len(emotions)
        }
