export interface DetectedEmotion {
  tristeza: number;
  desmotivación: number;
  búsqueda_motivación: number;
  preocupación: number;
}

export interface AIResponse {
  success: boolean;
  response?: string;
  error?: string;
  emotions: Record<string, number>;
  pdf_url?: string;
}

export interface UserPreferences {
  language?: string;
  theme?: 'light' | 'dark';
  fontSize?: number;
}

export interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
}

export interface VerseBoxType {
  text: string;
  reference: string;
  emotionalContext?: string;
}

export interface QuoteBoxType {
  text: string;
  source: string;
}