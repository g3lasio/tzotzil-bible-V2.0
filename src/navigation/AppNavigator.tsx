import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../contexts/AuthContext';
import { ActivityIndicator, View } from 'react-native';
import HomeScreen from '../screens/HomeScreen';
import BibleScreen from '../screens/BibleScreen';
import ChaptersScreen from '../screens/ChaptersScreen';
import VersesScreen from '../screens/VersesScreen';
import SearchScreen from '../screens/SearchScreen';
import NevinChatScreen from '../screens/NevinChatScreen';
import SettingsScreen from '../screens/SettingsScreen';
import AuthScreen from '../screens/AuthScreen';

import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';
import { useAuth } from '../hooks/useAuth';
import AuthScreen from '../screens/auth/AuthScreen';
import BibleScreen from '../screens/BibleScreen';
import ChaptersScreen from '../screens/ChaptersScreen';
import NevinChatScreen from '../screens/NevinChatScreen';
import SearchScreen from '../screens/SearchScreen';
import SettingsScreen from '../screens/SettingsScreen';
import HomeScreen from '../screens/HomeScreen';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const { token, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <Stack.Navigator initialRouteName={token ? "Home" : "Auth"}>
      {token ? (
        <>
          <Stack.Screen name="Home" component={HomeScreen} />
          <Stack.Screen name="Bible" component={BibleScreen} />
          <Stack.Screen name="Chapters" component={ChaptersScreen} />
          <Stack.Screen name="Verses" component={VersesScreen} />
          <Stack.Screen name="Search" component={SearchScreen} options={{ title: 'Buscar' }} />
          <Stack.Screen name="NevinChat" component={NevinChatScreen} options={{ title: 'Nevin AI' }} />
          <Stack.Screen name="Settings" component={SettingsScreen} options={{ title: 'Configuración' }} />
        </>
      ) : (
        <Stack.Screen 
          name="Auth" 
          component={AuthScreen} 
          options={{ headerShown: false }} 
        />
      )}
    </Stack.Navigator>
  );
}