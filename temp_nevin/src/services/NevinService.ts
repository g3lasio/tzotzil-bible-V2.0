import { OpenAIApi, Configuration } from 'openai';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import { DetectedEmotion, AIResponse, UserPreferences } from '../types/nevin';

class NevinService {
  private openai: OpenAIApi;
  private static CACHE_KEY = 'nevin_offline_data';


  constructor() {
    const configuration = new Configuration({
      apiKey: process.env.OPENAI_API_KEY,
    });
    this.openai = new OpenAIApi(configuration);
  }

  async initializeOfflineContent() {
    try {
      const contentExists = await AsyncStorage.getItem(NevinService.CACHE_KEY);
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

  async getAIResponse(
    question: string,
    context: string = "",
    language: string = "Spanish",
    userPreferences?: UserPreferences
  ): Promise<AIResponse> {
    try {
      const emotions = this.detectEmotion(question);
      const emotionalGuidance = this.getEmotionalGuidance(emotions);

      const prompt = `
        Eres Nevin, un asistente virtual amigable y empático que ayuda a encontrar respuestas en la Biblia.
        
        Contexto emocional:
        ${emotionalGuidance}
        
        Formato de respuesta:
        1. Para versículos bíblicos:
           <div class="verse-box">
           [Texto del versículo]
           <small class="verse-ref">[Libro Capítulo:Versículo]</small>
           </div>

        2. Para citas de Elena G. White:
           <div class="quote-box">
           [Texto de la cita]
           <small class="quote-ref">[Nombre del Libro, página]</small>
           </div>

        3. Para información importante:
           <div class="info-box">
           [Información relevante]
           </div>

        Responde en ${language} de manera profesional y estructurada.

        Conversación previa:
        ${context}

        Mensaje del usuario: ${question}
      `;

      const response = await this.openai.createChatCompletion({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "Eres Nevin, un asistente virtual amigable y empático que ayuda a encontrar respuestas bíblicas y comparte pensamientos inspiradores de literatura cristiana como complemento."
          },
          { role: "user", content: prompt }
        ]
      });

      const responseText = response.data.choices[0].message?.content || "";

      return {
        success: true,
        response: responseText,
        emotions
      };

    } catch (error) {
      console.error('Error in getAIResponse:', error);
      return {
        success: false,
        error: "Lo siento, hubo un error inesperado. Por favor, intenta nuevamente.",
        emotions: {}
      };
    }
  }
}

export const nevinService = new NevinService();