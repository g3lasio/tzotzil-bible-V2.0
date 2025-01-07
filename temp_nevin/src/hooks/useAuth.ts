import { useState, useEffect } from 'react';
import { LoginCredentials, RegisterCredentials, User } from '../types/auth';
import { AuthService } from '../services/AuthService';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const userData = await AuthService.getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error('Error checking auth status:', err);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      setError(null);
      const { user } = await AuthService.login(credentials.email, credentials.password);
      setUser(user);
    } catch (err) {
      setError('Error al iniciar sesión');
      throw err;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    try {
      setError(null);
      const { user } = await AuthService.register(credentials);
      setUser(user);
    } catch (err) {
      setError('Error al registrar usuario');
      throw err;
    }
  };

  const forgotPassword = async (email: string) => {
    try {
      setError(null);
      await AuthService.forgotPassword(email);
    } catch (err) {
      setError('Error al enviar el correo de recuperación');
      throw err;
    }
  };

  const resetPassword = async (code: string, password: string) => {
    try {
      setError(null);
      await AuthService.resetPassword(code, password);
    } catch (err) {
      setError('Error al restablecer la contraseña');
      throw err;
    }
  };

  const logout = async () => {
    try {
      await AuthService.logout();
      setUser(null);
    } catch (err) {
      console.error('Error logging out:', err);
      throw err;
    }
  };

  return {
    user,
    isAuthenticated: !!user,
    loading,
    error,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
  };
}