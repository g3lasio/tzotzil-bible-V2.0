import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Card, Text, Checkbox, ActivityIndicator } from 'react-native-paper';
import { BIBLE_API_URL } from '@env';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type SearchResult = {
  id: number;
  book: string;
  chapter: number;
  verse: number;
  tzotzil_text: string;
  spanish_text: string;
};

type SearchScreenProps = NativeStackScreenProps<any, 'Search'>;

export default function SearchScreen({ navigation }: SearchScreenProps) {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTzotzil, setSearchTzotzil] = useState(true);
  const [searchSpanish, setSearchSpanish] = useState(true);

  const handleSearch = async () => {
    if (!keyword.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const versions = [];
      if (searchTzotzil) versions.push('tzotzil');
      if (searchSpanish) versions.push('spanish');

      const queryParams = new URLSearchParams({
        keyword: keyword.trim(),
        ...versions.reduce((acc, v) => ({ ...acc, version: v }), {}),
      });

      const response = await fetch(`${BIBLE_API_URL}/api/bible/search?${queryParams}`);
      if (!response.ok) {
        throw new Error('Error en la búsqueda');
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error searching:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResultPress = (result: SearchResult) => {
    navigation.navigate('Verses', {
      book: result.book,
      chapter: result.chapter,
      initialVerse: result.verse,
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          value={keyword}
          onChangeText={setKeyword}
          placeholder="Buscar en la Biblia..."
          onSubmitEditing={handleSearch}
        />
        <View style={styles.checkboxContainer}>
          <Checkbox.Item
            label="Tzotzil"
            status={searchTzotzil ? 'checked' : 'unchecked'}
            onPress={() => setSearchTzotzil(!searchTzotzil)}
          />
          <Checkbox.Item
            label="Español"
            status={searchSpanish ? 'checked' : 'unchecked'}
            onPress={() => setSearchSpanish(!searchSpanish)}
          />
        </View>
        <Button
          mode="contained"
          onPress={handleSearch}
          loading={loading}
          disabled={loading || !keyword.trim()}
          style={styles.searchButton}
        >
          Buscar
        </Button>
      </View>

      {error && (
        <Text style={styles.errorText}>{error}</Text>
      )}

      {loading ? (
        <ActivityIndicator style={styles.loading} />
      ) : (
        <ScrollView style={styles.resultsContainer}>
          {results.map((result) => (
            <Card
              key={`${result.book}-${result.chapter}-${result.verse}`}
              style={styles.resultCard}
              onPress={() => handleResultPress(result)}
            >
              <Card.Content>
                <Text variant="titleMedium">
                  {result.book} {result.chapter}:{result.verse}
                </Text>
                {searchSpanish && (
                  <Text variant="bodyMedium" style={styles.spanishText}>
                    {result.spanish_text}
                  </Text>
                )}
                {searchTzotzil && (
                  <Text variant="bodyMedium" style={styles.tzotzilText}>
                    {result.tzotzil_text}
                  </Text>
                )}
              </Card.Content>
            </Card>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchContainer: {
    padding: 16,
    backgroundColor: '#fff',
    elevation: 4,
  },
  searchInput: {
    marginBottom: 8,
  },
  checkboxContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 8,
  },
  searchButton: {
    marginTop: 8,
  },
  loading: {
    marginTop: 20,
  },
  resultsContainer: {
    padding: 16,
  },
  resultCard: {
    marginBottom: 8,
  },
  spanishText: {
    marginTop: 8,
  },
  tzotzilText: {
    marginTop: 4,
    fontStyle: 'italic',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginTop: 16,
  },
});
