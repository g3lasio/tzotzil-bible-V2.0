import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Title, Card, Text, ActivityIndicator, TouchableRipple } from 'react-native-paper';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useApiWithCache } from '../hooks/useApiWithCache';

type Book = {
  name: string;
  chapters: number[];
};

type BibleScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Bible'>;
};

export default function BibleScreen({ navigation }: BibleScreenProps) {
  const { data: books, loading, error } = useApiWithCache<Book[]>({
    endpoint: '/api/bible/books',
    cacheKey: 'bible_books',
    expiresIn: 30 * 24 * 60 * 60 * 1000, // 30 días
  });

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