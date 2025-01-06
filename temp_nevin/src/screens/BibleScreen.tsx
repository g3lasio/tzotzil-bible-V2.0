
import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Card, Text, useTheme, ActivityIndicator, Searchbar } from 'react-native-paper';
import { databaseService } from '../services/DatabaseService';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';

type Book = {
  name: string;
  chapters: number;
};

type BibleScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Bible'>;
};

const BIBLE_BOOKS: Book[] = [
  { name: 'Génesis', chapters: 50 },
  { name: 'Éxodo', chapters: 40 },
  { name: 'Levítico', chapters: 27 },
  { name: 'Números', chapters: 36 },
  { name: 'Deuteronomio', chapters: 34 },
  // Add more books as needed
];

export default function BibleScreen({ navigation }: BibleScreenProps) {
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredBooks, setFilteredBooks] = useState(BIBLE_BOOKS);
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

  useEffect(() => {
    const filtered = BIBLE_BOOKS.filter(book => 
      book.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredBooks(filtered);
  }, [searchQuery]);

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
    <SafeAreaView style={styles.container}>
      <Searchbar
        placeholder="Buscar libro..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchBar}
      />
      <FlatList
        data={filteredBooks}
        renderItem={renderBookItem}
        keyExtractor={item => item.name}
        contentContainerStyle={styles.listContainer}
      />
    </SafeAreaView>
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
  searchBar: {
    margin: 16,
    elevation: 4,
  },
  listContainer: {
    padding: 16,
  },
  bookCard: {
    marginBottom: 12,
    elevation: 2,
  },
});
