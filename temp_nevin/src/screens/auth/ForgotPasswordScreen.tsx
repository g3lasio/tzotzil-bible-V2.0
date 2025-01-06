import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Button, TextInput, Text } from 'react-native-paper';
import { useAuth } from '../../hooks/useAuth';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

export default function ForgotPasswordScreen() {
  const [email, setEmail] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const { forgotPassword } = useAuth();
  const navigation = useNavigation<NativeStackNavigationProp<any>>();

  const handleResetPassword = async () => {
    try {
      setLoading(true);
      await forgotPassword(email);
      // Navegar a la pantalla de verificación o mostrar mensaje de éxito
      navigation.navigate('Login');
    } catch (error) {
      console.error('Error resetting password:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text variant="headlineMedium" style={styles.title}>
          Recuperar Contraseña
        </Text>
        
        <Text style={styles.description}>
          Ingresa tu correo electrónico y te enviaremos instrucciones para recuperar tu contraseña.
        </Text>
        
        <TextInput
          label="Email"
          value={email}
          onChangeText={setEmail}
          mode="outlined"
          keyboardType="email-address"
          autoCapitalize="none"
          style={styles.input}
        />
        
        <Button
          mode="contained"
          onPress={handleResetPassword}
          loading={loading}
          style={styles.button}
        >
          Enviar Instrucciones
        </Button>
        
        <Button
          mode="text"
          onPress={() => navigation.navigate('Login')}
          style={styles.link}
        >
          Volver al inicio de sesión
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
    marginBottom: 20,
  },
  description: {
    textAlign: 'center',
    marginBottom: 30,
    paddingHorizontal: 20,
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
