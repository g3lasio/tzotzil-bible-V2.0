
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import axios from 'axios';
import { API_URL } from '../config';

interface AuthResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
    preferences: any;
  };
}

export class AuthService {
  static async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password,
      });
      
      if (response.data.token) {
        await SecureStore.setItemAsync('user_token', response.data.token);
        await SecureStore.setItemAsync('user_data', JSON.stringify(response.data.user));
      }
      
      return response.data;
    } catch (error) {
      throw new Error('Error en la autenticación');
    }
  }

  static async authenticateWithBiometrics(): Promise<boolean> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();

      if (!hasHardware || !isEnrolled) {
        return false;
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Autenticación biométrica',
        fallbackLabel: 'Usar contraseña',
        cancelLabel: 'Cancelar',
        disableDeviceFallback: false,
      });

      return result.success;
    } catch (error) {
      console.error('Error en autenticación biométrica:', error);
      return false;
    }
  }

  static async loginWithBiometrics(): Promise<AuthResponse | null> {
    const isAuthenticated = await this.authenticateWithBiometrics();
    if (!isAuthenticated) {
      throw new Error('Autenticación biométrica fallida');
    }

    const storedToken = await SecureStore.getItemAsync('user_token');
    const storedUser = await SecureStore.getItemAsync('user_data');

    if (!storedToken || !storedUser) {
      throw new Error('No hay datos de sesión guardados');
    }

    return {
      token: storedToken,
      user: JSON.parse(storedUser)
    };
  }

  static async logout(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('user_token');
      await SecureStore.deleteItemAsync('user_data');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  }

  static async getCurrentUser(): Promise<any> {
    try {
      const userData = await SecureStore.getItemAsync('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      return null;
    }
  }

  static async isAuthenticated(): Promise<boolean> {
    const token = await SecureStore.getItemAsync('user_token');
    return !!token;
  }

  static async refreshToken(): Promise<void> {
    const token = await SecureStore.getItemAsync('user_token');
    if (!token) return;

    try {
      const response = await axios.post(`${API_URL}/api/auth/refresh`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.token) {
        await SecureStore.setItemAsync('user_token', response.data.token);
      }
    } catch (error) {
      await this.logout();
      throw new Error('Sesión expirada');
    }
  }
}
