import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Text, ActivityIndicator, Divider } from 'react-native-paper';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BIBLE_API_URL } from '@env';

type VersesScreenProps = NativeStackScreenProps<any, 'Verses'>;

type Verse = {
  verse: number;
  spanish_text: string;
  tzotzil_text: string;
};

export default function VersesScreen({ route }: VersesScreenProps) {
  const { book, chapter } = route.params;
  const [loading, setLoading] = useState(true);
  const [verses, setVerses] = useState<Verse[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVerses();
  }, [book, chapter]);

  const fetchVerses = async () => {
    try {
      const response = await fetch(
        `${BIBLE_API_URL}/api/bible/verses/${encodeURIComponent(book)}/${chapter}`
      );
      if (!response.ok) {
        throw new Error('Error al cargar los versículos');
      }
      const data = await response.json();
      setVerses(data.verses);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error fetching verses:', err);
    } finally {
      setLoading(false);
    }
  };

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
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {verses.map((verse) => (
          <Card key={verse.verse} style={styles.verseCard}>
            <Card.Content>
              <Text variant="titleMedium" style={styles.verseNumber}>
                {verse.verse}
              </Text>
              <Text variant="bodyLarge" style={styles.spanishText}>
                {verse.spanish_text}
              </Text>
              <Divider style={styles.divider} />
              <Text variant="bodyMedium" style={styles.tzotzilText}>
                {verse.tzotzil_text}
              </Text>
            </Card.Content>
          </Card>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 10,
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
  verseCard: {
    marginBottom: 10,
    elevation: 2,
  },
  verseNumber: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  spanishText: {
    marginBottom: 8,
  },
  tzotzilText: {
    fontStyle: 'italic',
  },
  divider: {
    marginVertical: 8,
  },
});
