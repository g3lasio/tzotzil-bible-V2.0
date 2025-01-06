import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Button, TextInput, Text } from 'react-native-paper';
import { useAuth } from '../../hooks/useAuth';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { LoginCredentials } from '../../types/auth';

export default function LoginScreen() {
  const [credentials, setCredentials] = React.useState<LoginCredentials>({
    email: '',
    password: '',
    rememberMe: false
  });
  const [loading, setLoading] = React.useState(false);
  const { login } = useAuth();
  const navigation = useNavigation<NativeStackNavigationProp<any>>();

  const handleLogin = async () => {
    try {
      setLoading(true);
      await login(credentials);
    } catch (error) {
      console.error('Error logging in:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text variant="headlineMedium" style={styles.title}>
          Iniciar Sesión
        </Text>
        
        <TextInput
          label="Email"
          value={credentials.email}
          onChangeText={(text) => setCredentials(prev => ({ ...prev, email: text }))}
          mode="outlined"
          keyboardType="email-address"
          autoCapitalize="none"
          style={styles.input}
        />
        
        <TextInput
          label="Contraseña"
          value={credentials.password}
          onChangeText={(text) => setCredentials(prev => ({ ...prev, password: text }))}
          mode="outlined"
          secureTextEntry
          style={styles.input}
        />
        
        <Button
          mode="contained"
          onPress={handleLogin}
          loading={loading}
          style={styles.button}
        >
          Iniciar Sesión
        </Button>
        
        <Button
          mode="text"
          onPress={() => navigation.navigate('Register')}
          style={styles.link}
        >
          ¿No tienes cuenta? Regístrate
        </Button>
        
        <Button
          mode="text"
          onPress={() => navigation.navigate('ForgotPassword')}
          style={styles.link}
        >
          ¿Olvidaste tu contraseña?
        </Button>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    textAlign: 'center',
    marginBottom: 30,
  },
  input: {
    marginBottom: 15,
  },
  button: {
    marginTop: 10,
    paddingVertical: 8,
  },
  link: {
    marginTop: 15,
  },
});
