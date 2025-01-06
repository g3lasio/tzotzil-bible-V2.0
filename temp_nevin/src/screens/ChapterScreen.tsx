
import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Title, Card, Text } from 'react-native-paper';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type ChapterScreenProps = NativeStackScreenProps<any, 'Chapter'>;

export default function ChapterScreen({ route, navigation }: ChapterScreenProps) {
  const { book, totalChapters } = route.params;

  const handleChapterSelect = (chapter: number) => {
    navigation.navigate('Verses', { book, chapter });
  };

  return (
    <ScrollView style={styles.container}>
      <Title style={styles.title}>{book}</Title>
      <View style={styles.chaptersGrid}>
        {[...Array(totalChapters)].map((_, index) => (
          <Card
            key={index}
            style={styles.chapterCard}
            onPress={() => handleChapterSelect(index + 1)}
          >
            <Card.Content>
              <Text style={styles.chapterNumber}>{index + 1}</Text>
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
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginVertical: 20,
  },
  chaptersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
    justifyContent: 'center',
  },
  chapterCard: {
    width: 70,
    height: 70,
    margin: 8,
  },
  chapterNumber: {
    textAlign: 'center',
    fontSize: 20,
  },
});
