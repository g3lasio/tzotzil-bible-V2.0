
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
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
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
  emotions?: DetectedEmotion;
}

export interface DetectedEmotion {
  tristeza: number;
  desmotivación: number;
  búsqueda_motivación: number;
  preocupación: number;
}
