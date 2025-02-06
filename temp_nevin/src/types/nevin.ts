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