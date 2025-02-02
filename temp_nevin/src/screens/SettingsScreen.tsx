
import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { List, Switch, Button, Divider, Title, Text, useTheme, IconButton } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../hooks/useAuth';
import DonationModal from '../components/DonationModal';
import { PaymentService } from '../services/PaymentService';

export default function SettingsScreen() {
  const [darkMode, setDarkMode] = useState(false);
  const [offlineMode, setOfflineMode] = useState(false);
  const [bilingualMode, setBilingualMode] = useState(true);
  const [autoPlay, setAutoPlay] = useState(false);
  const [fontSize, setFontSize] = useState('medium');
  const [showDonationModal, setShowDonationModal] = useState(false);
  const theme = useTheme();
  const { logout } = useAuth();

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const settings = await AsyncStorage.getItem('userSettings');
      if (settings) {
        const parsed = JSON.parse(settings);
        setDarkMode(parsed.darkMode ?? false);
        setOfflineMode(parsed.offlineMode ?? false);
        setBilingualMode(parsed.bilingualMode ?? true);
        setAutoPlay(parsed.autoPlay ?? false);
        setFontSize(parsed.fontSize ?? 'medium');
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const saveSettings = async (key: string, value: any) => {
    try {
      const settings = await AsyncStorage.getItem('userSettings');
      const currentSettings = settings ? JSON.parse(settings) : {};
      const newSettings = { ...currentSettings, [key]: value };
      await AsyncStorage.setItem('userSettings', JSON.stringify(newSettings));
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Cerrar Sesión',
      '¿Estás seguro que deseas cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Cerrar Sesión',
          onPress: async () => {
            await logout();
          },
          style: 'destructive'
        }
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Title style={styles.title}>Configuración</Title>

      <List.Section>
        <List.Subheader>Apariencia</List.Subheader>
        <List.Item
          title="Modo Oscuro"
          left={props => <List.Icon {...props} icon="theme-light-dark" />}
          right={() => (
            <Switch
              value={darkMode}
              onValueChange={(value) => {
                setDarkMode(value);
                saveSettings('darkMode', value);
              }}
            />
          )}
        />
        <List.Item
          title="Tamaño de Fuente"
          description="Ajusta el tamaño del texto"
          left={props => <List.Icon {...props} icon="format-size" />}
          right={() => (
            <View style={styles.fontSizeControl}>
              <IconButton icon="minus" onPress={() => setFontSize('small')} />
              <Text>A</Text>
              <IconButton icon="plus" onPress={() => setFontSize('large')} />
            </View>
          )}
        />
      </List.Section>

      <Divider />

      <List.Section>
        <List.Subheader>Contenido</List.Subheader>
        <List.Item
          title="Modo Bilingüe"
          description="Mostrar texto en español y tzotzil"
          left={props => <List.Icon {...props} icon="translate" />}
          right={() => (
            <Switch
              value={bilingualMode}
              onValueChange={(value) => {
                setBilingualMode(value);
                saveSettings('bilingualMode', value);
              }}
            />
          )}
        />
        <List.Item
          title="Modo Sin Conexión"
          description="Descargar contenido para uso sin internet"
          left={props => <List.Icon {...props} icon="wifi-off" />}
          right={() => (
            <Switch
              value={offlineMode}
              onValueChange={(value) => {
                setOfflineMode(value);
                saveSettings('offlineMode', value);
              }}
            />
          )}
        />
        <List.Item
          title="Auto-reproducción"
          description="Reproducir audio automáticamente"
          left={props => <List.Icon {...props} icon="play-circle" />}
          right={() => (
            <Switch
              value={autoPlay}
              onValueChange={(value) => {
                setAutoPlay(value);
                saveSettings('autoPlay', value);
              }}
            />
          )}
        />
      </List.Section>

      <View style={styles.donateContainer}>
        <Text style={styles.donateText}>
          Ayúdanos a mantener y mejorar esta aplicación para seguir compartiendo la Palabra de Dios
        </Text>
        <Button 
          mode="contained"
          onPress={() => setShowDonationModal(true)}
          style={styles.donateButton}
          icon="heart"
        >
          Realizar Donación
        </Button>
      </View>

      <Button 
        mode="outlined" 
        onPress={handleLogout}
        style={styles.logoutButton}
        icon="logout"
      >
        Cerrar Sesión
      </Button>

      <DonationModal
        visible={showDonationModal}
        onDismiss={() => setShowDonationModal(false)}
        onDonationComplete={() => {
          setShowDonationModal(false);
          Alert.alert('¡Gracias!', 'Tu donación nos ayuda a seguir mejorando.');
        }}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginVertical: 20,
  },
  fontSizeControl: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  donateContainer: {
    padding: 16,
    alignItems: 'center',
    marginTop: 20,
  },
  donateText: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#666',
  },
  donateButton: {
    width: '80%',
    marginBottom: 10,
  },
  logoutButton: {
    margin: 16,
    marginTop: 0,
  }
});
