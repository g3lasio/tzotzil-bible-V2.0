
import React, { useState, useEffect } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { Text, Card, Searchbar, ActivityIndicator, useTheme } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { commonStyles } from '../styles/common';

export default function BibleScreen({ navigation }) {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [books, setBooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const renderBookItem = ({ item }) => (
    <Card 
      style={styles.bookCard}
      onPress={() => navigation.navigate('Chapter', { bookId: item.id })}
    >
      <Card.Content>
        <Text style={styles.bookTitle}>{item.name}</Text>
        <Text style={styles.chapterCount}>{item.chapters} capítulos</Text>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Searchbar
        placeholder="Buscar libro..."
        value={searchQuery}
        onChangeText={setSearchQuery}
        style={styles.searchBar}
      />
      <FlatList
        data={books}
        renderItem={renderBookItem}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.listContainer}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    ...commonStyles.container,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchBar: {
    margin: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
  },
  listContainer: {
    padding: theme.spacing.md,
  },
  bookCard: {
    ...commonStyles.card,
  },
  bookTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  chapterCount: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  }
});;
