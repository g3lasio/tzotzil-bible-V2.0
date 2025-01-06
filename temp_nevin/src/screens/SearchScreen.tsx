import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, TextInput, Button, Checkbox, Card, ActivityIndicator, SegmentedButtons } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api } from '../services/api';
import { useNavigation } from '@react-navigation/native';
import { SearchResult, SearchParams } from '../types/search';
import { books } from '../constants/bible';

export default function SearchScreen() {
  const [searchParams, setSearchParams] = useState<SearchParams>({
    keyword: '',
    versions: {
      tzotzil: true,
      spanish: false,
    },
    book: 'all',
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const navigation = useNavigation();

  const handleSearch = async () => {
    if (!searchParams.keyword.trim()) {
      return;
    }

    try {
      setLoading(true);
      const response = await api.get<{ results: SearchResult[] }>('/search', { 
        params: {
          keyword: searchParams.keyword,
          version: Object.entries(searchParams.versions)
            .filter(([_, value]) => value)
            .map(([key]) => key),
          book: searchParams.book,
        }
      });
      setResults(response.data.results);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = (language: 'tzotzil' | 'spanish') => {
    setSearchParams(prev => ({
      ...prev,
      versions: {
        ...prev.versions,
        [language]: !prev.versions[language],
      }
    }));
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text variant="headlineMedium" style={styles.title}>
          Búsqueda Bíblica
        </Text>
        <Text style={styles.subtitle}>
          Busca versículos en Tzotzil y Español
        </Text>

        <Card style={styles.searchCard}>
          <Card.Content>
            <TextInput
              label="Buscar versículo, palabra clave o referencia..."
              value={searchParams.keyword}
              onChangeText={(text) => setSearchParams(prev => ({ ...prev, keyword: text }))}
              mode="outlined"
              style={styles.input}
              right={loading ? <TextInput.Icon icon="loading" /> : undefined}
            />

            <View style={styles.filtersContainer}>
              <Text variant="titleMedium" style={styles.filterTitle}>Idiomas</Text>
              <View style={styles.checkboxContainer}>
                <Checkbox.Android
                  status={searchParams.versions.tzotzil ? 'checked' : 'unchecked'}
                  onPress={() => handleLanguageChange('tzotzil')}
                />
                <Text>Tzotzil</Text>
              </View>
              <View style={styles.checkboxContainer}>
                <Checkbox.Android
                  status={searchParams.versions.spanish ? 'checked' : 'unchecked'}
                  onPress={() => handleLanguageChange('spanish')}
                />
                <Text>Español</Text>
              </View>

              <Text variant="titleMedium" style={[styles.filterTitle, styles.marginTop]}>
                Libro
              </Text>
              <SegmentedButtons
                value={searchParams.book}
                onValueChange={(value) => 
                  setSearchParams(prev => ({ ...prev, book: value }))
                }
                buttons={[
                  { value: 'all', label: 'Todos' },
                  ...books.map(book => ({
                    value: book,
                    label: book,
                  }))
                ]}
                style={styles.segmentedButtons}
              />
            </View>

            <Button
              mode="contained"
              onPress={handleSearch}
              loading={loading}
              style={styles.button}
              disabled={!searchParams.keyword.trim() || 
                (!searchParams.versions.tzotzil && !searchParams.versions.spanish)}
            >
              Buscar
            </Button>
          </Card.Content>
        </Card>

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" />
            <Text style={styles.loadingText}>Buscando versículos...</Text>
          </View>
        )}

        {results.map((result, index) => (
          <Card key={index} style={styles.resultCard}>
            <Card.Content>
              <Text variant="titleMedium">{result.reference}</Text>
              <Text style={styles.verseText}>{result.text}</Text>
              <Text variant="labelSmall" style={styles.versionText}>
                {result.version === 'tzotzil' ? 'Tzotzil' : 'Español'}
              </Text>
            </Card.Content>
          </Card>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    padding: 20,
  },
  title: {
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 30,
    opacity: 0.7,
  },
  searchCard: {
    marginBottom: 20,
  },
  input: {
    marginBottom: 15,
  },
  filtersContainer: {
    marginBottom: 15,
  },
  filterTitle: {
    marginBottom: 10,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  marginTop: {
    marginTop: 15,
  },
  segmentedButtons: {
    marginTop: 5,
  },
  button: {
    marginTop: 10,
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
  },
  resultCard: {
    marginBottom: 10,
  },
  verseText: {
    marginTop: 5,
  },
  versionText: {
    marginTop: 5,
    opacity: 0.7,
  },
});