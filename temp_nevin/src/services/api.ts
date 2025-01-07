import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// Configuración base de la API según la plataforma
const BASE_URL = Platform.select({
  web: 'http://localhost:5000',
  default: 'http://10.0.2.2:5000', // Para emulador Android
});

// Crear instancia de axios con configuración base
export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token de autenticación
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('user_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      await SecureStore.deleteItemAsync('user_token');
      await SecureStore.deleteItemAsync('user_data');
      // Aquí podrías disparar un evento para redireccionar al login
      if (typeof window !== 'undefined') { //Check if it is a browser environment
          window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);