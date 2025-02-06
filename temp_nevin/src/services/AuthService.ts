import * as SecureStore from 'expo-secure-store';
import axios from 'axios';
import { API_URL } from '../config';
import { LoginCredentials, RegisterCredentials, User } from '../types/auth';

export class AuthService {
  static async login(credentials: LoginCredentials): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, credentials);
      if (response.data.token) {
        await SecureStore.setItemAsync('token', response.data.token);
        await SecureStore.setItemAsync('user', JSON.stringify(response.data.user));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      throw new Error('Error en inicio de sesión');
    }
  }

  static async register(credentials: RegisterCredentials): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, credentials);
      if (response.data.token) {
        await SecureStore.setItemAsync('token', response.data.token);
        await SecureStore.setItemAsync('user', JSON.stringify(response.data.user));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Register error:', error);
      throw new Error('Error en registro');
    }
  }

  static async logout(): Promise<void> {
    await SecureStore.deleteItemAsync('token');
    await SecureStore.deleteItemAsync('user');
  }

  static async getCurrentUser(): Promise<User | null> {
    try {
      const userStr = await SecureStore.getItemAsync('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  }

  static async isAuthenticated(): Promise<boolean> {
    const token = await SecureStore.getItemAsync('token');
    return !!token;
  }
}