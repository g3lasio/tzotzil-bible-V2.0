import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import axios from 'axios';
import { API_URL } from '../config';
import { LoginCredentials, RegisterCredentials, User } from '../types/auth';

interface AuthResponse {
  token: string;
  user: User;
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

  static async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${API_URL}/api/auth/register`, credentials);

      if (response.data.token) {
        await SecureStore.setItemAsync('user_token', response.data.token);
        await SecureStore.setItemAsync('user_data', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw new Error('Error en el registro');
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

  static async forgotPassword(email: string): Promise<void> {
    try {
      await axios.post(`${API_URL}/api/auth/forgot_password`, { email });
    } catch (error) {
      throw new Error('Error al solicitar recuperación de contraseña');
    }
  }

  static async resetPassword(code: string, password: string): Promise<void> {
    try {
      await axios.post(`${API_URL}/api/auth/reset_password`, { code, password });
    } catch (error) {
      throw new Error('Error al restablecer la contraseña');
    }
  }

  static async logout(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('user_token');
      await SecureStore.deleteItemAsync('user_data');
      await axios.post(`${API_URL}/api/auth/logout`);
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
      // Asegurarse de eliminar los datos locales incluso si la petición falla
      await SecureStore.deleteItemAsync('user_token');
      await SecureStore.deleteItemAsync('user_data');
    }
  }

  static async getCurrentUser(): Promise<User | null> {
    try {
      const userData = await SecureStore.getItemAsync('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error al obtener usuario actual:', error);
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