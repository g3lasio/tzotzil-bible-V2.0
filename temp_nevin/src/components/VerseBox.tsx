import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { VerseBoxType } from '../types/nevin';

interface VerseBoxProps {
  verse: VerseBoxType;
}

export const VerseBox: React.FC<VerseBoxProps> = ({ verse }) => {
  const theme = useTheme();

  const getEmphasisStyle = () => {
    const emphasisMap: Record<string, any> = {
      tristeza: styles.comfortVerse,
      ansiedad: styles.peaceVerse,
      duda: styles.faithVerse,
      gratitud: styles.praiseVerse,
      arrepentimiento: styles.forgivenessVerse,
    };
    return verse.emotionalContext ? emphasisMap[verse.emotionalContext] : {};
  };

  return (
    <View style={[styles.container, getEmphasisStyle()]}>
      <Text style={[styles.verseContent, { color: theme.colors.onSurface }]}>
        {verse.text}
      </Text>
      <Text style={[styles.verseRef, { color: theme.colors.onSurfaceVariant }]}>
        {verse.reference}
      </Text>
      {verse.emotionalContext && (
        <Text style={[styles.contextInsight, { color: theme.colors.onSurfaceVariant }]}>
          {getContextualInsight(verse.emotionalContext)}
        </Text>
      )}
    </View>
  );
};

const getContextualInsight = (emotion: string): string => {
  const insights: Record<string, string> = {
    tristeza: "Este versículo nos recuerda el consuelo divino en momentos difíciles",
    ansiedad: "Encontramos paz al confiar en las promesas de Dios",
    duda: "La fe se fortalece al meditar en la palabra de Dios",
    gratitud: "Expresemos nuestra gratitud por las bendiciones recibidas",
    arrepentimiento: "El amor de Dios nos ofrece perdón y renovación"
  };
  return insights[emotion] || '';
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 8,
    marginVertical: 8,
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    borderLeftWidth: 4,
    borderLeftColor: '#ffd700',
  },
  verseContent: {
    fontSize: 16,
    lineHeight: 24,
    fontStyle: 'italic',
  },
  verseRef: {
    marginTop: 8,
    fontSize: 12,
  },
  contextInsight: {
    marginTop: 8,
    fontSize: 14,
    fontStyle: 'italic',
  },
  comfortVerse: {
    borderLeftColor: '#4A90E2',
    backgroundColor: 'rgba(74, 144, 226, 0.1)',
  },
  peaceVerse: {
    borderLeftColor: '#2ECC71',
    backgroundColor: 'rgba(46, 204, 113, 0.1)',
  },
  faithVerse: {
    borderLeftColor: '#F1C40F',
    backgroundColor: 'rgba(241, 196, 15, 0.1)',
  },
  praiseVerse: {
    borderLeftColor: '#9B59B6',
    backgroundColor: 'rgba(155, 89, 182, 0.1)',
  },
  forgivenessVerse: {
    borderLeftColor: '#E74C3C',
    backgroundColor: 'rgba(231, 76, 60, 0.1)',
  },
});

export default VerseBox;