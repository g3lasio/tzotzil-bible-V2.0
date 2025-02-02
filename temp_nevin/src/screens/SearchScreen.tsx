import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, TextInput, Button, Card, useTheme, ActivityIndicator } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { BibleService } from '../services/BibleService';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type SearchScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Search'>;
};

export default function SearchScreen({ navigation }: SearchScreenProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const theme = useTheme();

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const results = await BibleService.searchVerses(searchQuery);
      setSearchResults(results);
    } catch (error) {
      console.error('Error searching verses:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigateToVerse = (book: string, chapter: number, verse: number) => {
    navigation.navigate('Verses', { book, chapter, initialVerse: verse });
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          mode="outlined"
          placeholder="Buscar versículos..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          style={styles.searchInput}
          returnKeyType="search"
          onSubmitEditing={handleSearch}
        />
        <Button 
          mode="contained" 
          onPress={handleSearch}
          style={styles.searchButton}
          disabled={loading}
        >
          Buscar
        </Button>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      ) : (
        <ScrollView style={styles.resultsContainer}>
          {searchResults.map((result, index) => (
            <Card
              key={index}
              style={styles.resultCard}
              onPress={() => navigateToVerse(result.book, result.chapter, result.verse)}
            >
              <Card.Content>
                <Text variant="titleMedium">
                  {result.book} {result.chapter}:{result.verse}
                </Text>
                <Text variant="bodyMedium" style={styles.verseText}>
                  {result.text}
                </Text>
              </Card.Content>
            </Card>
          ))}
          {searchResults.length === 0 && searchQuery && !loading && (
            <Text style={styles.noResults}>
              No se encontraron resultados para "{searchQuery}"
            </Text>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchContainer: {
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  searchInput: {
    flex: 1,
  },
  searchButton: {
    minWidth: 100,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  resultsContainer: {
    flex: 1,
    padding: 16,
  },
  resultCard: {
    marginBottom: 12,
    elevation: 2,
  },
  verseText: {
    marginTop: 8,
  },
  noResults: {
    textAlign: 'center',
    marginTop: 24,
    color: '#666',
  },
});