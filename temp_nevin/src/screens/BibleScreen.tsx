
import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, ActivityIndicator } from 'react-native';
import { Title, Card, Text, useTheme } from 'react-native-paper';
import { databaseService } from '../services/DatabaseService';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type BibleScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Bible'>;
};

type Book = {
  name: string;
  chapters: number;
};

const BIBLE_BOOKS: Book[] = [
  { name: 'Génesis', chapters: 50 },
  { name: 'Éxodo', chapters: 40 },
  { name: 'Levítico', chapters: 27 },
  // Añadir más libros según sea necesario
];

export default function BibleScreen({ navigation }: BibleScreenProps) {
  const [loading, setLoading] = useState(true);
  const theme = useTheme();

  useEffect(() => {
    const initializeBooks = async () => {
      try {
        await databaseService.initDatabase();
        setLoading(false);
      } catch (error) {
        console.error('Error loading books:', error);
        setLoading(false);
      }
    };

    initializeBooks();
  }, []);

  const handleBookSelect = (book: Book) => {
    navigation.navigate('Chapter', { book: book.name, totalChapters: book.chapters });
  };

  const renderBookItem = ({ item }: { item: Book }) => (
    <Card
      style={styles.bookCard}
      onPress={() => handleBookSelect(item)}
    >
      <Card.Content>
        <Text variant="titleMedium">{item.name}</Text>
        <Text variant="bodyMedium">{item.chapters} capítulos</Text>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Title style={styles.title}>Biblia</Title>
      <FlatList
        data={BIBLE_BOOKS}
        renderItem={renderBookItem}
        keyExtractor={(item) => item.name}
        numColumns={2}
        contentContainerStyle={styles.listContainer}
      />
    </View>
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
  listContainer: {
    paddingBottom: 16,
  },
  bookCard: {
    flex: 1,
    margin: 8,
    elevation: 2,
  },
});
