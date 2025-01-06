import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

type User = {
  id: number;
  username: string;
  email: string;
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  loading: boolean;
  signIn: (token: string, userData: User) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const [storedToken, storedUser] = await Promise.all([
        AsyncStorage.getItem('authToken'),
        AsyncStorage.getItem('userData'),
      ]);

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error('Error loading auth data:', error);
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (newToken: string, userData: User) => {
    try {
      await Promise.all([
        AsyncStorage.setItem('authToken', newToken),
        AsyncStorage.setItem('userData', JSON.stringify(userData)),
      ]);
      setToken(newToken);
      setUser(userData);
    } catch (error) {
      console.error('Error storing auth data:', error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await Promise.all([
        AsyncStorage.removeItem('authToken'),
        AsyncStorage.removeItem('userData'),
      ]);
      setToken(null);
      setUser(null);
    } catch (error) {
      console.error('Error removing auth data:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
