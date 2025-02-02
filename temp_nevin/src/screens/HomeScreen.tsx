import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Button, useTheme } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

export default function HomeScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<any>>();
  const theme = useTheme();

  const navigateToScreen = (screenName: string) => {
    navigation.navigate(screenName);
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.surface]}
        style={styles.gradient}
      >
        <Text style={styles.title}>Sistema Nevin</Text>
        <Text style={styles.subtitle}>Biblia Tzotzil - Español</Text>

        <View style={styles.cardsContainer}>
          <Card style={styles.card} onPress={() => navigateToScreen('Bible')}>
            <Card.Content>
              <Text variant="titleLarge">Biblia</Text>
              <Text variant="bodyMedium">
                Lee la Biblia en Tzotzil y Español
              </Text>
            </Card.Content>
          </Card>

          <Card style={styles.card} onPress={() => navigateToScreen('Nevin')}>
            <Card.Content>
              <Text variant="titleLarge">Nevin AI</Text>
              <Text variant="bodyMedium">
                Consulta con nuestro asistente bíblico
              </Text>
            </Card.Content>
          </Card>

          <Card style={styles.card} onPress={() => navigateToScreen('Search')}>
            <Card.Content>
              <Text variant="titleLarge">Búsqueda</Text>
              <Text variant="bodyMedium">
                Busca versículos por palabra o referencia
              </Text>
            </Card.Content>
          </Card>
        </View>

        <Button
          mode="contained"
          onPress={() => navigateToScreen('Settings')}
          style={styles.settingsButton}
        >
          Configuración
        </Button>
      </LinearGradient>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
    padding: 16,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 40,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#fff',
    marginTop: 8,
    marginBottom: 32,
    textAlign: 'center',
  },
  cardsContainer: {
    width: '100%',
    gap: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  settingsButton: {
    marginTop: 24,
    width: '80%',
  },
});