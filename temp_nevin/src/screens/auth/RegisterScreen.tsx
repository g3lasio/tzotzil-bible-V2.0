import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Button, TextInput, Text, Checkbox } from 'react-native-paper';
import { useAuth } from '../../hooks/useAuth';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RegisterCredentials } from '../../types/auth';

export default function RegisterScreen() {
  const [credentials, setCredentials] = React.useState<RegisterCredentials>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    terms: false
  });
  const [loading, setLoading] = React.useState(false);
  const { register } = useAuth();
  const navigation = useNavigation<NativeStackNavigationProp<any>>();

  const handleRegister = async () => {
    try {
      setLoading(true);
      await register(credentials);
    } catch (error) {
      console.error('Error registering:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <Text variant="headlineMedium" style={styles.title}>
            Crear Cuenta
          </Text>
          
          <TextInput
            label="Nombre de usuario"
            value={credentials.username}
            onChangeText={(text) => setCredentials(prev => ({ ...prev, username: text }))}
            mode="outlined"
            style={styles.input}
          />
          
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
          
          <TextInput
            label="Confirmar Contraseña"
            value={credentials.confirmPassword}
            onChangeText={(text) => setCredentials(prev => ({ ...prev, confirmPassword: text }))}
            mode="outlined"
            secureTextEntry
            style={styles.input}
          />

          <View style={styles.checkboxContainer}>
            <Checkbox.Android
              status={credentials.terms ? 'checked' : 'unchecked'}
              onPress={() => setCredentials(prev => ({ ...prev, terms: !prev.terms }))}
            />
            <Text>Acepto los términos y condiciones</Text>
          </View>
          
          <Button
            mode="contained"
            onPress={handleRegister}
            loading={loading}
            style={styles.button}
            disabled={!credentials.terms}
          >
            Registrarse
          </Button>
          
          <Button
            mode="text"
            onPress={() => navigation.navigate('Login')}
            style={styles.link}
          >
            ¿Ya tienes cuenta? Inicia sesión
          </Button>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    flexGrow: 1,
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
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
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
