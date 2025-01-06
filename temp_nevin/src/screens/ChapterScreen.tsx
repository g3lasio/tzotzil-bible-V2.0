
import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, ActivityIndicator, useTheme } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { databaseService } from '../services/DatabaseService';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type ChapterScreenProps = NativeStackScreenProps<any, 'Chapter'>;

type Verse = {
  verse: number;
  tzotzil_text: string;
  spanish_text: string;
};

export default function ChapterScreen({ route, navigation }: ChapterScreenProps) {
  const [verses, setVerses] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(true);
  const { book, chapter = 1 } = route.params;
  const theme = useTheme();

  useEffect(() => {
    const loadVerses = async () => {
      try {
        const verseData = await databaseService.getVerses(book, chapter);
        setVerses(verseData);
      } catch (error) {
        console.error('Error loading verses:', error);
      } finally {
        setLoading(false);
      }
    };

    loadVerses();
  }, [book, chapter]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>{book} {chapter}</Text>
        {verses.map((verse) => (
          <Card key={verse.verse} style={styles.verseCard}>
            <Card.Content>
              <Text variant="bodyLarge" style={styles.verseNumber}>
                {verse.verse}
              </Text>
              <Text variant="bodyMedium" style={styles.tzotzilText}>
                {verse.tzotzil_text}
              </Text>
              <Text variant="bodyMedium" style={styles.spanishText}>
                {verse.spanish_text}
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
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContent: {
    padding: 16,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
  },
  verseCard: {
    marginBottom: 12,
    elevation: 2,
  },
  verseNumber: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  tzotzilText: {
    marginBottom: 8,
  },
  spanishText: {
    fontStyle: 'italic',
  },
});
