import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Title, Card, Paragraph, Button, ActivityIndicator } from 'react-native-paper';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type BibleScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Bible'>;
};

export default function BibleScreen({ navigation }: BibleScreenProps) {
  const [loading, setLoading] = useState(true);
  const [books, setBooks] = useState<any[]>([]);

  useEffect(() => {
    // Aquí implementaremos la carga de libros desde la API
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Title style={styles.title}>Biblia</Title>
      <View style={styles.booksContainer}>
        {/* Aquí irá la lista de libros */}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginVertical: 20,
  },
  booksContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
});
