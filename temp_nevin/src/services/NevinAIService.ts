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

      const response = await api.post('/nevin/chat', {
        message,
        context,
        chat_history: chatHistory.map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content
        }))
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      return {
        success: true,
        response: response.data.response,
        emotions: response.data.emotions || {}
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