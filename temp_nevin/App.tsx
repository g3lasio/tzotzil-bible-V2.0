
import 'react-native-gesture-handler';
import { NavigationContainer } from '@react-navigation/native';
import { Provider as PaperProvider } from 'react-native-paper';
import AppNavigator from './src/navigation/AppNavigator';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect } from 'react';
import * as SQLite from 'expo-sqlite';

const queryClient = new QueryClient();

export default function App() {
  useEffect(() => {
    const initializeDatabase = async () => {
      const db = SQLite.openDatabase('bible.db');
      // Inicializar tablas locales aquí
    };
    initializeDatabase();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <PaperProvider>
        <NavigationContainer>
          <AppNavigator />
          <StatusBar style="auto" />
        </NavigationContainer>
      </PaperProvider>
    </QueryClientProvider>
  );
}
