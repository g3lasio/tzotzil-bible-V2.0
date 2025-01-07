import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button, Checkbox, Card, ActivityIndicator, SegmentedButtons, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api } from '../services/api';
import { useApiWithCache } from '../hooks/useApiWithCache';
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
  const [showFilters, setShowFilters] = useState(false);

  // Asegurarse de que al menos una versión esté seleccionada
  const handleVersionChange = (version: 'tzotzil' | 'spanish') => {
    const otherVersion = version === 'tzotzil' ? 'spanish' : 'tzotzil';
    setSearchParams(prev => ({
      ...prev,
      versions: {
        ...prev.versions,
        [version]: !prev.versions[version],
        // Si se está desmarcando la única versión seleccionada, marcar la otra
        [otherVersion]: prev.versions[version] && !prev.versions[otherVersion] 
          ? true 
          : prev.versions[otherVersion]
      }
    }));
  };

  const handleSearch = async () => {
    if (!searchParams.keyword.trim()) return;

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

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardAvoid}
      >
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
                right={loading ? <TextInput.Icon icon="loading" /> : 
                  <TextInput.Icon icon="magnify" onPress={handleSearch} />}
                onSubmitEditing={handleSearch}
              />

              <Button
                mode="outlined"
                onPress={() => setShowFilters(!showFilters)}
                icon={showFilters ? "chevron-up" : "chevron-down"}
                style={styles.filterButton}
              >
                Filtros de búsqueda
              </Button>

              {showFilters && (
                <View style={styles.filtersContainer}>
                  <Text variant="titleMedium" style={styles.filterTitle}>
                    Idiomas
                  </Text>
                  <View style={styles.languageContainer}>
                    <Chip
                      selected={searchParams.versions.tzotzil}
                      onPress={() => handleVersionChange('tzotzil')}
                      style={styles.chip}
                    >
                      Tzotzil
                    </Chip>
                    <Chip
                      selected={searchParams.versions.spanish}
                      onPress={() => handleVersionChange('spanish')}
                      style={styles.chip}
                    >
                      Español
                    </Chip>
                  </View>

                  <Text variant="titleMedium" style={[styles.filterTitle, styles.marginTop]}>
                    Libro
                  </Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                    <SegmentedButtons
                      value={searchParams.book}
                      onValueChange={(value) => setSearchParams(prev => ({ ...prev, book: value }))}
                      buttons={[
                        { value: 'all', label: 'Todos' },
                        ...books.map(book => ({
                          value: book,
                          label: book,
                        }))
                      ]}
                      style={styles.segmentedButtons}
                    />
                  </ScrollView>
                </View>
              )}

              <Button
                mode="contained"
                onPress={handleSearch}
                loading={loading}
                style={styles.searchButton}
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
                <Text variant="titleMedium" style={styles.referenceText}>
                  {result.reference}
                </Text>
                <Text style={styles.verseText}>{result.text}</Text>
                <Text variant="labelSmall" style={styles.versionText}>
                  {result.version === 'tzotzil' ? 'Tzotzil' : 'Español'}
                </Text>
              </Card.Content>
            </Card>
          ))}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  keyboardAvoid: {
    flex: 1,
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
  filterButton: {
    marginBottom: 10,
  },
  filtersContainer: {
    marginBottom: 15,
  },
  filterTitle: {
    marginBottom: 10,
  },
  languageContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 15,
  },
  chip: {
    marginRight: 8,
  },
  marginTop: {
    marginTop: 15,
  },
  segmentedButtons: {
    marginTop: 5,
  },
  searchButton: {
    marginTop: 15,
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
  referenceText: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  verseText: {
    marginTop: 5,
    lineHeight: 22,
  },
  versionText: {
    marginTop: 5,
    opacity: 0.7,
  },
});