import { OpenAIApi, Configuration } from 'openai';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import { DetectedEmotion, AIResponse, UserPreferences, ChatMessage } from '../types/nevin';
import { api } from './api';

class NevinService {
  private openai: OpenAIApi;
  private static readonly CHAT_HISTORY_KEY = 'nevin_chat_history';

  constructor() {
    const configuration = new Configuration({
      apiKey: process.env.OPENAI_API_KEY,
    });
    this.openai = new OpenAIApi(configuration);
  }

  async initializeOfflineContent() {
    try {
      const contentExists = await AsyncStorage.getItem(NevinService.CHAT_HISTORY_KEY);
      if (!contentExists) {
        await this.downloadInitialContent();
      }
    } catch (error) {
      console.error('Offline content initialization error:', error);
    }
  }

  private async downloadInitialContent() {
    // Implementar lógica de descarga inicial de contenido
  }

  private detectEmotion(text: string): Record<string, number> {
    const emotionPatterns = {
      tristeza: ['triste', 'deprimido', 'solo', 'dolor', 'pena', 'angustia', 'desesperado'],
      desmotivación: ['cansado', 'sin ganas', 'difícil', 'no puedo', 'rendirme', 'fracaso'],
      búsqueda_motivación: ['ayuda', 'necesito fuerza', 'animo', 'esperanza', 'consejo'],
      preocupación: ['preocupado', 'ansioso', 'miedo', 'inquieto', 'nervioso']
    };

    const textLower = text.toLowerCase();
    const emotions: Record<string, number> = {};

    Object.entries(emotionPatterns).forEach(([emotion, keywords]) => {
      const score = keywords.reduce((count, keyword) =>
        textLower.includes(keyword) ? count + 1 : count, 0);
      emotions[emotion] = score > 0 ? score / keywords.length : 0;
    });

    return emotions;
  }

  private getEmotionalGuidance(emotions: Record<string, number>): string {
    const highestEmotion = Object.entries(emotions)
      .reduce((max, [emotion, score]) =>
        score > (max[1] || 0) ? [emotion, score] : max, ['', 0]);

    const guidanceMap: Record<string, string> = {
      tristeza: "El usuario parece estar triste o afligido. Proporciona una respuesta compasiva y alentadora, usando versículos bíblicos de consuelo.",
      desmotivación: "El usuario parece estar desmotivado. Ofrece palabras de ánimo y versículos que hablen sobre la fortaleza en Dios.",
      búsqueda_motivación: "El usuario está buscando motivación. Comparte versículos inspiradores y mensajes de esperanza.",
      preocupación: "El usuario muestra preocupación. Ofrece versículos sobre la paz de Dios y Su cuidado."
    };

    return highestEmotion[1] > 0.3 ? guidanceMap[highestEmotion[0]] : "";
  }

  static async getToken(): Promise<string | null> {
    return await AsyncStorage.getItem('user_token');
  }

  static async sendMessage(
    message: string,
    chatHistory: ChatMessage[] = []
  ): Promise<AIResponse> {
    try {
      const token = await this.getToken();

      if (!token) {
        return {
          success: false,
          error: 'No se encontró el token de autenticación',
          emotions: {}
        };
      }

      const response = await api.post('/nevin/chat', {
        message,
        chat_history: chatHistory.map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content
        }))
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      return {
        success: true,
        response: response.data.response,
        emotions: response.data.emotions || {}
      };

    } catch (error) {
      console.error('Error en NevinService.sendMessage:', error);
      return {
        success: false,
        error: "Lo siento, hubo un error procesando tu mensaje. Por favor, intenta nuevamente.",
        emotions: {}
      };
    }
  }

  static async loadChatHistory(): Promise<ChatMessage[]> {
    try {
      const history = await AsyncStorage.getItem(this.CHAT_HISTORY_KEY);
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.error('Error cargando historial del chat:', error);
      return [];
    }
  }

  static async saveChatHistory(messages: ChatMessage[]): Promise<void> {
    try {
      await AsyncStorage.setItem(this.CHAT_HISTORY_KEY, JSON.stringify(messages));
    } catch (error) {
      console.error('Error guardando historial del chat:', error);
    }
  }

  static async clearChatHistory(): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.CHAT_HISTORY_KEY);
    } catch (error) {
      console.error('Error limpiando historial del chat:', error);
    }
  }
}

export const nevinService = new NevinService();