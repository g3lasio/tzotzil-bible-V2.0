import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { List, Switch, Button, Divider, Title, Text } from 'react-native-paper';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import DonationModal from '../components/DonationModal';

type SettingsScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Settings'>;
};

export default function SettingsScreen({ navigation }: SettingsScreenProps) {
  const [darkMode, setDarkMode] = useState(false);
  const [offlineMode, setOfflineMode] = useState(false);
  const [bilingualMode, setBilingualMode] = useState(true);
  const [showDonationModal, setShowDonationModal] = useState(false);

  const handleDonationComplete = () => {
    setShowDonationModal(false);
    // Mostrar mensaje de agradecimiento
  };

  return (
    <ScrollView style={styles.container}>
      <Title style={styles.title}>Configuración</Title>

      <List.Section>
        <List.Subheader>Apariencia</List.Subheader>
        <List.Item
          title="Modo Oscuro"
          right={() => (
            <Switch
              value={darkMode}
              onValueChange={setDarkMode}
            />
          )}
        />
      </List.Section>

      <Divider />

      <List.Section>
        <List.Subheader>Contenido</List.Subheader>
        <List.Item
          title="Modo Bilingüe"
          description="Mostrar texto en español y tzotzil"
          right={() => (
            <Switch
              value={bilingualMode}
              onValueChange={setBilingualMode}
            />
          )}
        />
        <List.Item
          title="Modo Offline"
          description="Descargar contenido para uso sin conexión"
          right={() => (
            <Switch
              value={offlineMode}
              onValueChange={setOfflineMode}
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

      <DonationModal
        visible={showDonationModal}
        onDismiss={() => setShowDonationModal(false)}
        onDonationComplete={handleDonationComplete}
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
  donateContainer: {
    padding: 16,
    alignItems: 'center',
  },
  donateText: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#666',
  },
  donateButton: {
    width: '80%',
  },
});