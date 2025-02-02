
import React, { useEffect, useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, ActivityIndicator, FAB, useTheme } from 'react-native-paper';
import { useRoute, useNavigation } from '@react-navigation/native';
import { BibleService } from '../services/BibleService';
import VerseBox from '../components/VerseBox';
import type { BibleVerse } from '../types/bible';

export default function ChapterScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation();
  const theme = useTheme();
  const { book, chapter } = route.params;
  
  const [verses, setVerses] = useState<BibleVerse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVerses();
  }, [book, chapter]);

  const loadVerses = async () => {
    try {
      setLoading(true);
      const versesData = await BibleService.getVerses(book, chapter);
      setVerses(versesData);
      setError(null);
    } catch (err) {
      setError('Error cargando versículos');
      console.error('Error loading verses:', err);
    } finally {
      setLoading(false);
    }
  };

  const navigateToNextChapter = () => {
    navigation.setParams({ chapter: chapter + 1 });
  };

  const navigateToPreviousChapter = () => {
    if (chapter > 1) {
      navigation.setParams({ chapter: chapter - 1 });
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <Text style={styles.header}>{book} {chapter}</Text>
        {verses.map((verse) => (
          <VerseBox key={verse.id} verse={verse} />
        ))}
      </ScrollView>
      
      <FAB
        icon="chevron-left"
        style={[styles.fab, styles.fabLeft]}
        onPress={navigateToPreviousChapter}
        disabled={chapter <= 1}
      />
      
      <FAB
        icon="chevron-right"
        style={[styles.fab, styles.fabRight]}
        onPress={navigateToNextChapter}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  fab: {
    position: 'absolute',
    bottom: 16,
  },
  fabLeft: {
    left: 16,
  },
  fabRight: {
    right: 16,
  }
});
