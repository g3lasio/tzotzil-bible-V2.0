import OpenAI from 'openai';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AIResponse, ChatMessage, DetectedEmotion } from '../types/nevin';
import axios from 'axios';
import { API_URL } from '../config';

export class NevinAIService {
  private static openai: OpenAI;
  private static systemPrompt = `Eres Nevin, un asistente pastoral y bíblico cálido y sabio que valora la concisión. 
    Tu propósito es ayudar a las personas a comprender mejor la Biblia y conectar emocionalmente con ellas.`;

  static async initialize() {
    const apiKey = await AsyncStorage.getItem('OPENAI_API_KEY');
    if (!apiKey) {
      throw new Error('OpenAI API key no encontrada');
    }
    this.openai = new OpenAI({ apiKey });
  }

  static async detectEmotion(text: string): Promise<DetectedEmotion> {
    const emotionPatterns = {
      tristeza: ['triste', 'deprimido', 'solo', 'dolor', 'pena', 'angustia', 'desesperado', 'sufrimiento'],
      desmotivación: ['cansado', 'sin ganas', 'difícil', 'no puedo', 'rendirme', 'fracaso', 'desánimo'],
      búsqueda_motivación: ['ayuda', 'necesito fuerza', 'animo', 'esperanza', 'consejo', 'guía'],
      preocupación: ['preocupado', 'ansioso', 'miedo', 'inquieto', 'nervioso', 'incertidumbre']
    };

    const textLower = text.toLowerCase();
    const emotions: DetectedEmotion = {
      tristeza: 0,
      desmotivación: 0,
      búsqueda_motivación: 0,
      preocupación: 0
    };

    Object.entries(emotionPatterns).forEach(([emotion, patterns]) => {
      const matches = patterns.filter(pattern => textLower.includes(pattern));
      emotions[emotion as keyof DetectedEmotion] = matches.length / patterns.length;
    });

    return emotions;
  }

  static async processQuery(
    question: string,
    context: string = "",
    previousMessages: ChatMessage[] = []
  ): Promise<AIResponse> {
    try {
      const emotions = await this.detectEmotion(question);
      const token = await AsyncStorage.getItem('user_token');

      // Intenta primero con el backend
      try {
        const response = await axios.post(
          `${API_URL}/nevin/query`,
          {
            question,
            context,
            emotions
          },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        return response.data;
      } catch (backendError) {
        console.warn('Error con el backend, usando fallback local:', backendError);
      }

      // Fallback local usando OpenAI directamente
      if (!this.openai) await this.initialize();

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: this.systemPrompt },
          ...previousMessages.map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
          })),
          { role: "user", content: question }
        ],
        temperature: 0.7,
      });

      return {
        success: true,
        response: completion.choices[0]?.message?.content || "",
        emotions
      };

    } catch (error) {
      console.error('Error procesando consulta:', error);
      return {
        success: false,
        error: "Hubo un error procesando tu consulta. Por favor, intenta nuevamente.",
        emotions: await this.detectEmotion(question)
      };
    }
  }

  static async cacheResponse(question: string, response: AIResponse): Promise<void> {
    try {
      const cachedResponses = await AsyncStorage.getItem('cached_responses');
      const responses = cachedResponses ? JSON.parse(cachedResponses) : {};
      responses[question] = {
        ...response,
        timestamp: new Date().toISOString()
      };
      await AsyncStorage.setItem('cached_responses', JSON.stringify(responses));
    } catch (error) {
      console.error('Error cacheando respuesta:', error);
    }
  }

  static async getCachedResponse(question: string): Promise<AIResponse | null> {
    try {
      const cachedResponses = await AsyncStorage.getItem('cached_responses');
      if (!cachedResponses) return null;

      const responses = JSON.parse(cachedResponses);
      return responses[question] || null;
    } catch (error) {
      console.error('Error obteniendo respuesta cacheada:', error);
      return null;
    }
  }
}