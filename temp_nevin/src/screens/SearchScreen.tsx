import React, { useState, useCallback } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button, Card, ActivityIndicator, SegmentedButtons, Chip, IconButton } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api } from '../services/api';
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

  const handleVersionChange = useCallback((version: 'tzotzil' | 'spanish') => {
    const otherVersion = version === 'tzotzil' ? 'spanish' : 'tzotzil';
    setSearchParams(prev => ({
      ...prev,
      versions: {
        ...prev.versions,
        [version]: !prev.versions[version],
        [otherVersion]: prev.versions[version] && !prev.versions[otherVersion] 
          ? true 
          : prev.versions[otherVersion]
      }
    }));
  }, []);

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

  const renderSearchBar = () => (
    <Card style={styles.searchCard}>
      <Card.Content>
        <View style={styles.searchInputContainer}>
          <TextInput
            label="Buscar en la Biblia"
            placeholder="Versículo, palabra clave o referencia..."
            value={searchParams.keyword}
            onChangeText={(text) => setSearchParams(prev => ({ ...prev, keyword: text }))}
            mode="outlined"
            style={styles.searchInput}
            right={<TextInput.Icon icon={loading ? "loading" : "magnify"} onPress={handleSearch} />}
            onSubmitEditing={handleSearch}
          />
        </View>

        <Button
          mode="outlined"
          onPress={() => setShowFilters(!showFilters)}
          icon={showFilters ? "chevron-up" : "chevron-down"}
          style={styles.filterToggleButton}
        >
          {showFilters ? "Ocultar filtros" : "Mostrar filtros"}
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
                showSelectedCheck
              >
                Tzotzil
              </Chip>
              <Chip
                selected={searchParams.versions.spanish}
                onPress={() => handleVersionChange('spanish')}
                style={styles.chip}
                showSelectedCheck
              >
                Español
              </Chip>
            </View>

            <Text variant="titleMedium" style={[styles.filterTitle, styles.marginTop]}>
              Libro
            </Text>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false}
              style={styles.booksScrollView}
            >
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
  );

  const renderResults = () => (
    <>
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
          <Text style={styles.loadingText}>Buscando versículos...</Text>
        </View>
      )}

      {results.map((result, index) => (
        <Card key={index} style={styles.resultCard}>
          <Card.Content>
            <View style={styles.resultHeader}>
              <Text variant="titleMedium" style={styles.referenceText}>
                {result.reference}
              </Text>
              <Chip compact>{result.version === 'tzotzil' ? 'Tzotzil' : 'Español'}</Chip>
            </View>
            <Text style={styles.verseText}>{result.text}</Text>
          </Card.Content>
        </Card>
      ))}
    </>
  );

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardAvoid}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <Text variant="headlineMedium" style={styles.title}>
            Búsqueda Bíblica
          </Text>
          <Text style={styles.subtitle}>
            Busca versículos en Tzotzil y Español
          </Text>

          {renderSearchBar()}
          {renderResults()}
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
    padding: 16,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 24,
    opacity: 0.7,
  },
  searchCard: {
    marginBottom: 16,
    elevation: 2,
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  searchInput: {
    flex: 1,
  },
  filterToggleButton: {
    marginTop: 12,
  },
  filtersContainer: {
    marginTop: 16,
  },
  filterTitle: {
    marginBottom: 8,
  },
  languageContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  marginTop: {
    marginTop: 16,
  },
  booksScrollView: {
    marginBottom: 16,
  },
  segmentedButtons: {
    marginTop: 4,
  },
  searchButton: {
    marginTop: 16,
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 24,
  },
  loadingText: {
    marginTop: 8,
  },
  resultCard: {
    marginBottom: 12,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  referenceText: {
    flex: 1,
    fontWeight: 'bold',
  },
  verseText: {
    fontSize: 16,
    lineHeight: 24,
  }
});