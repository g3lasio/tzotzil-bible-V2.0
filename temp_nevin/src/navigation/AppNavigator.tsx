import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../hooks/useAuth';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import ForgotPasswordScreen from '../screens/auth/ForgotPasswordScreen';
import HomeScreen from '../screens/HomeScreen';
import BibleScreen from '../screens/BibleScreen';
import ChapterScreen from '../screens/ChapterScreen';
import SearchScreen from '../screens/SearchScreen';
import NevinScreen from '../screens/NevinScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const { isAuthenticated } = useAuth();

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{
        headerShown: false,
        animation: 'slide_from_right'
      }}>
        {!isAuthenticated ? (
          // Auth Stack
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
            <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
          </>
        ) : (
          // Main App Stack
          <>
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="Bible" component={BibleScreen} />
            <Stack.Screen name="Chapter" component={ChapterScreen} />
            <Stack.Screen name="Search" component={SearchScreen} />
            <Stack.Screen name="Nevin" component={NevinScreen} />
            <Stack.Screen name="Settings" component={SettingsScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}