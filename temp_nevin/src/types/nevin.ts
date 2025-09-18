export interface User {
  id: string;
  username: string;
  email: string;
  preferences: UserPreferences;
  subscription: SubscriptionStatus;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  fontSize: number;
  language: 'es' | 'tzo';
  notifications: boolean;
}

export interface SubscriptionStatus {
  type: 'free' | 'premium';
  expiresAt: string;
  features: string[];
}

export interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
}

export interface BibleVerse {
  book: string;
  chapter: number;
  verse: number;
  tzotzilText: string;
  spanishText: string;
}

export interface AIResponse {
  success: boolean;
  response?: string;
  error?: string;
  emotions: DetectedEmotions;
  metadata?: {
    system_version?: string;
    powered_by?: string;
    text_type?: string;
    hermeneutic_principles?: string[];
  };
  egw_sources?: Array<{
    title: string;
    url: string;
    snippet: string;
  }>;
  doctrinal_validation?: {
    status: string;
    principles_applied: string[];
    warnings?: string[];
  };
}

export interface DetectedEmotions {
  tristeza?: number;
  desmotivacion?: number;
  busqueda_motivacion?: number;
  preocupacion?: number;
}

export interface NevinState {
  currentEmotion: string;
  chatHistory: ChatMessage[];
  isProcessing: boolean;
}