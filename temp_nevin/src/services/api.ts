import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Crear instancia de axios con configuración base
export const api = axios.create({
  baseURL: 'http://localhost:5000', // URL del servidor Flask
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token de autenticación
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('auth_token');
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
      await SecureStore.deleteItemAsync('auth_token');
      // Aquí podrías redirigir al login si lo necesitas
    }
    return Promise.reject(error);
  }
);
