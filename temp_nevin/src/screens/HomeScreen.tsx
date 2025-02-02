
import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button, useTheme, Surface } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { BibleService } from '../services/BibleService';

export default function HomeScreen() {
  const navigation = useNavigation();
  const theme = useTheme();
  const [dailyPromise, setDailyPromise] = useState('');

  useEffect(() => {
    loadDailyPromise();
  }, []);

  const loadDailyPromise = async () => {
    try {
      const promise = await BibleService.getRandomPromise();
      setDailyPromise(promise);
    } catch (error) {
      console.error('Error loading daily promise:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.surface]}
        style={styles.gradient}
      >
        <Surface style={styles.promiseCard}>
          <Text style={styles.promiseTitle}>Promesa del día</Text>
          <Text style={styles.promiseText}>{dailyPromise}</Text>
          <Button 
            mode="outlined" 
            onPress={() => {/* Implementar compartir */}}
            style={styles.shareButton}
          >
            Compartir
          </Button>
        </Surface>

        <View style={styles.menuGrid}>
          <Card style={styles.menuCard} onPress={() => navigation.navigate('Bible')}>
            <Card.Content>
              <Text variant="titleLarge">Biblia</Text>
              <Text variant="bodyMedium">Lee la Biblia en Tzotzil y Español</Text>
            </Card.Content>
          </Card>

          <Card style={styles.menuCard} onPress={() => navigation.navigate('Nevin')}>
            <Card.Content>
              <Text variant="titleLarge">Nevin AI</Text>
              <Text variant="bodyMedium">Consulta con nuestro asistente bíblico</Text>
            </Card.Content>
          </Card>

          <Card style={styles.menuCard} onPress={() => navigation.navigate('Search')}>
            <Card.Content>
              <Text variant="titleLarge">Búsqueda</Text>
              <Text variant="bodyMedium">Busca versículos por palabra o referencia</Text>
            </Card.Content>
          </Card>
        </View>
      </LinearGradient>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    padding: 16,
    minHeight: '100%',
  },
  promiseCard: {
    padding: 20,
    marginVertical: 20,
    borderRadius: 10,
    elevation: 4,
  },
  promiseTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
  },
  promiseText: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 16,
  },
  shareButton: {
    marginTop: 8,
  },
  menuGrid: {
    gap: 16,
  },
  menuCard: {
    marginBottom: 16,
    elevation: 4,
  },
});
