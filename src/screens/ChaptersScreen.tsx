import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Title, Card, Text, ActivityIndicator, TouchableRipple } from 'react-native-paper';
import { BIBLE_API_URL } from '@env';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type ChaptersScreenProps = NativeStackScreenProps<any, 'Chapters'>;

type Chapter = {
  number: number;
  verses: number;
};

export default function ChaptersScreen({ route, navigation }: ChaptersScreenProps) {
  const { book } = route.params;
  const [loading, setLoading] = useState(true);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    navigation.setOptions({
      title: book
    });
    fetchChapters();
  }, [book]);

  const fetchChapters = async () => {
    try {
      const response = await fetch(`${BIBLE_API_URL}/api/bible/chapters/${encodeURIComponent(book)}`);
      if (!response.ok) {
        throw new Error('Error al cargar los capítulos');
      }
      const data = await response.json();
      const formattedChapters = Object.entries(data.chapters).map(([number, verses]) => ({
        number: parseInt(number),
        verses
      }));
      setChapters(formattedChapters);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error fetching chapters:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChapterPress = (chapter: Chapter) => {
    navigation.navigate('Verses', {
      book,
      chapter: chapter.number
    });
  };

  const renderChapter = ({ item }: { item: Chapter }) => (
    <TouchableRipple
      onPress={() => handleChapterPress(item)}
      style={styles.chapterCard}
    >
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge" style={styles.chapterNumber}>{item.number}</Text>
          <Text variant="bodySmall">{item.verses} versículos</Text>
        </Card.Content>
      </Card>
    </TouchableRipple>
  );

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
    <View style={styles.container}>
      <Title style={styles.title}>Capítulos de {book}</Title>
      <FlatList
        data={chapters}
        renderItem={renderChapter}
        keyExtractor={(item) => item.number.toString()}
        numColumns={3}
        contentContainerStyle={styles.chaptersContainer}
      />
    </View>
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
  title: {
    fontSize: 20,
    textAlign: 'center',
    marginVertical: 15,
    fontWeight: 'bold',
  },
  chaptersContainer: {
    padding: 10,
  },
  chapterCard: {
    flex: 1,
    margin: 5,
  },
  card: {
    elevation: 4,
  },
  chapterNumber: {
    textAlign: 'center',
    fontWeight: 'bold',
  },
});
