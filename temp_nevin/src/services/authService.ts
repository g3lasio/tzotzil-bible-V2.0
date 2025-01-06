import { LoginCredentials, RegisterCredentials, User } from '../types/auth';
import { api } from './api';

export const authService = {
  async login(credentials: LoginCredentials) {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  async register(credentials: RegisterCredentials) {
    const response = await api.post('/auth/register', credentials);
    return response.data;
  },

  async logout() {
    await api.post('/auth/logout');
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async forgotPassword(email: string) {
    const response = await api.post('/auth/forgot_password', { email });
    return response.data;
  },

  async resetPassword(code: string, password: string) {
    const response = await api.post('/auth/reset_password', { code, password });
    return response.data;
  }
};
