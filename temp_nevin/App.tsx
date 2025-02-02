
import 'react-native-gesture-handler';
import { NavigationContainer } from '@react-navigation/native';
import { Provider as PaperProvider } from 'react-native-paper';
import AppNavigator from './src/navigation/AppNavigator';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect } from 'react';
import { databaseService } from './src/services/DatabaseService';

const queryClient = new QueryClient();

export default function App() {
  useEffect(() => {
    const initializeApp = async () => {
      try {
        const dbInitialized = await databaseService.initDatabase();
        if (!dbInitialized) {
          console.error('Failed to initialize database');
        }
      } catch (error) {
        console.error('Error initializing app:', error);
      }
    };
    initializeApp();
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
