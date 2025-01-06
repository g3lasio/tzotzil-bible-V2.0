import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Title, Card, Text, ActivityIndicator, TouchableRipple } from 'react-native-paper';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { BIBLE_API_URL } from '@env';

type Book = {
  name: string;
  chapters: number[];
};

type BibleScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Bible'>;
};

export default function BibleScreen({ navigation }: BibleScreenProps) {
  const [loading, setLoading] = useState(true);
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const response = await fetch(`${BIBLE_API_URL}/api/bible/books`);
      if (!response.ok) {
        throw new Error('Error al cargar los libros');
      }
      const data = await response.json();
      setBooks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error fetching books:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBookPress = (book: Book) => {
    navigation.navigate('Chapters', { book: book.name });
  };

  const renderBook = ({ item }: { item: Book }) => (
    <TouchableRipple
      onPress={() => handleBookPress(item)}
      style={styles.bookCard}
    >
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">{item.name}</Text>
        </Card.Content>
      </Card>
    </TouchableRipple>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Title style={styles.title}>Biblia</Title>
      <FlatList
        data={books}
        renderItem={renderBook}
        keyExtractor={(item) => item.name}
        numColumns={2}
        contentContainerStyle={styles.booksContainer}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginVertical: 20,
    fontWeight: 'bold',
  },
  booksContainer: {
    padding: 10,
  },
  bookCard: {
    flex: 1,
    margin: 5,
  },
  card: {
    elevation: 4,
  },
});