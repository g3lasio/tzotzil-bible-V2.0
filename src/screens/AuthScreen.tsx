import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Surface } from 'react-native-paper';
import { BIBLE_API_URL } from '@env';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type AuthScreenProps = NativeStackScreenProps<any, 'Auth'>;

export default function AuthScreen({ navigation }: AuthScreenProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {
    if (!email.trim() || !password.trim() || (!isLogin && !username.trim())) {
      setError('Por favor completa todos los campos');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const endpoint = isLogin ? 'login' : 'register';
      const response = await fetch(`${BIBLE_API_URL}/api/auth/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          ...(isLogin ? {} : { username }),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Error en autenticación');
      }

      await AsyncStorage.setItem('authToken', data.token);
      await AsyncStorage.setItem('userData', JSON.stringify(data.user));

      navigation.replace('Home');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error de autenticación');
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <Surface style={styles.surface}>
        <Text variant="headlineMedium" style={styles.title}>
          {isLogin ? 'Iniciar Sesión' : 'Registrarse'}
        </Text>

        {error && (
          <Text style={styles.errorText}>{error}</Text>
        )}

        {!isLogin && (
          <TextInput
            style={styles.input}
            label="Nombre de usuario"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            disabled={loading}
          />
        )}

        <TextInput
          style={styles.input}
          label="Correo electrónico"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          disabled={loading}
        />

        <TextInput
          style={styles.input}
          label="Contraseña"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          disabled={loading}
        />

        <Button
          mode="contained"
          onPress={handleAuth}
          loading={loading}
          disabled={loading}
          style={styles.button}
        >
          {isLogin ? 'Iniciar Sesión' : 'Registrarse'}
        </Button>

        <Button
          mode="text"
          onPress={() => setIsLogin(!isLogin)}
          disabled={loading}
        >
          {isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
        </Button>
      </Surface>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    padding: 16,
  },
  surface: {
    padding: 20,
    borderRadius: 8,
    elevation: 4,
  },
  title: {
    textAlign: 'center',
    marginBottom: 24,
  },
  input: {
    marginBottom: 16,
    backgroundColor: '#fff',
  },
  button: {
    marginTop: 8,
    marginBottom: 16,
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 16,
  },
});
