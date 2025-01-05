import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Button, Title, Card } from 'react-native-paper';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type HomeScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Home'>;
};

export default function HomeScreen({ navigation }: HomeScreenProps) {
  return (
    <View style={styles.container}>
      <Title style={styles.title}>Bienvenido a Nevin</Title>
      
      <Card style={styles.card}>
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
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginVertical: 20,
  },
  card: {
    marginVertical: 10,
  },
  button: {
    marginVertical: 8,
  },
});
