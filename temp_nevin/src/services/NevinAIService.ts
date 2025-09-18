import { api } from './api';
import { AIResponse, ChatMessage } from '../types/nevin';
import AsyncStorage from '@react-native-async-storage/async-storage';

export class NevinAIService {
  private static readonly CHAT_HISTORY_KEY = 'nevin_chat_history';

  static async processQuery(
    message: string,
    context: string = '',
    chatHistory: ChatMessage[] = []
  ): Promise<AIResponse> {
    try {
      const token = await AsyncStorage.getItem('user_token');

      if (!token) {
        return {
          success: false,
          error: 'No se encontró el token de autenticación',
          emotions: {}
        };
      }

      // Use the revolutionary Nevin AI system with Claude 4 + EGW search + doctrinal validation
      const response = await api.post('/api/nevin/chat/revolutionary', {
        question: message,
        context,
        language: 'Spanish',
        extended_thinking: true,
        chat_history: chatHistory.map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content
        }))
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      return {
        success: true,
        response: response.data.response,
        emotions: response.data.emotions || {},
        metadata: response.data.metadata || {
          system_version: "Revolutionary Nevin AI v2.0",
          powered_by: "Claude 4 + EGW Web Search + Doctrinal Validation"
        },
        egw_sources: response.data.egw_sources || [],
        doctrinal_validation: response.data.doctrinal_validation || {}
      };
    } catch (error) {
      console.error('Error en NevinAIService.processQuery:', error);
      return {
        success: false,
        error: 'Hubo un error procesando tu mensaje',
        emotions: {}
      };
    }
  }

  static async loadChatHistory(): Promise<ChatMessage[]> {
    try {
      const history = await AsyncStorage.getItem(this.CHAT_HISTORY_KEY);
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.error('Error cargando historial:', error);
      return [];
    }
  }

  static async saveChatHistory(messages: ChatMessage[]): Promise<void> {
    try {
      await AsyncStorage.setItem(this.CHAT_HISTORY_KEY, JSON.stringify(messages));
    } catch (error) {
      console.error('Error guardando historial:', error);
    }
  }

  static async clearChatHistory(): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.CHAT_HISTORY_KEY);
    } catch (error) {
      console.error('Error limpiando historial:', error);
    }
  }
}