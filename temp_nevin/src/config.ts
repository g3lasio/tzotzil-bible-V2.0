import { API_URL as BACKEND_URL } from '@env';

// API Configuration
export const API_URL = BACKEND_URL || 'http://localhost:5000';

// Authentication Configuration
export const AUTH_CONFIG = {
  tokenKey: 'user_token',
  userDataKey: 'user_data',
  refreshTokenKey: 'refresh_token',
};

// OpenAI Configuration
export const AI_CONFIG = {
  modelName: 'gpt-4',
  temperature: 0.7,
  maxTokens: 2500,
};

// App Configuration
export const APP_CONFIG = {
  defaultLanguage: 'es',
  cacheExpiration: 24 * 60 * 60 * 1000, // 24 hours
  offlineMode: {
    enabled: true,
    maxCacheSize: 100 * 1024 * 1024, // 100MB
  },
};

// Navigation Configuration
export const ROUTES = {
  HOME: 'Home',
  CHAT: 'Chat',
  BIBLE: 'Bible',
  SETTINGS: 'Settings',
  AUTH: {
    LOGIN: 'Login',
    REGISTER: 'Register',
  },
};

// Feature Flags
export const FEATURES = {
  offlineMode: true,
  emotionDetection: true,
  bibleIntegration: true,
  donations: true,
};
