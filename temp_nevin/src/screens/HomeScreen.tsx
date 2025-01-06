
import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Share, Animated } from 'react-native';
import { Button, Title, Card, Text } from 'react-native-paper';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { LinearGradient } from 'expo-linear-gradient';

type HomeScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Home'>;
};

export default function HomeScreen({ navigation }: HomeScreenProps) {
  const [dailyPromise, setDailyPromise] = useState('');
  
  const handleShare = async () => {
    try {
      await Share.share({
        message: `${dailyPromise}\nby Tzotzil Bible`,
      });
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    // TODO: Implementar obtención de promesa diaria desde el backend
    setDailyPromise("Ejemplo de promesa diaria");
  }, []);

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a1a', '#2d2d2d']}
        style={styles.gradient}
      >
        <Title style={styles.title}>Bienvenido a Nevin</Title>
        
        <Card style={styles.promiseCard}>
          <Card.Content>
            <Title style={styles.promiseTitle}>Promesa del día</Title>
            <Text style={styles.promiseText}>{dailyPromise}</Text>
            <Button 
              mode="outlined" 
              onPress={handleShare}
              style={styles.shareButton}
              icon="share"
            >
              Compartir
            </Button>
          </Card.Content>
        </Card>

        <Card style={styles.menuCard}>
          <Card.Content>
            <Button 
              mode="contained" 
              onPress={() => navigation.navigate('Bible')}
              style={styles.button}
            >
              Leer Biblia
            </Button>
            
            <Button 
              mode="contained" 
              onPress={() => navigation.navigate('Chat')}
              style={styles.button}
            >
              Chat con Nevin
            </Button>
            
            <Button 
              mode="contained" 
              onPress={() => navigation.navigate('Settings')}
              style={styles.button}
            >
              Configuración
            </Button>
          </Card.Content>
        </Card>
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
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginVertical: 20,
    color: '#fff',
  },
  promiseCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    marginVertical: 20,
    borderRadius: 15,
  },
  promiseTitle: {
    fontSize: 20,
    textAlign: 'center',
    color: '#00ffcc',
  },
  promiseText: {
    textAlign: 'center',
    marginVertical: 10,
    fontSize: 16,
  },
  shareButton: {
    marginTop: 10,
    borderColor: '#00ffcc',
  },
  menuCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    marginTop: 20,
  },
  button: {
    marginVertical: 8,
    backgroundColor: '#00ffcc',
  },
});
