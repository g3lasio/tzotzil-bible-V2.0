import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { QuoteBoxType } from '../types/nevin';

interface QuoteBoxProps {
  quote: QuoteBoxType;
}

export const QuoteBox: React.FC<QuoteBoxProps> = ({ quote }) => {
  const theme = useTheme();

  return (
    <View style={[styles.container, { borderColor: theme.colors.surfaceVariant }]}>
      <Text style={[styles.quoteText, { color: theme.colors.onSurface }]}>
        {quote.text}
      </Text>
      <Text style={[styles.quoteSource, { color: theme.colors.onSurfaceVariant }]}>
        {quote.source}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 8,
    marginVertical: 8,
    backgroundColor: 'rgba(173, 181, 189, 0.1)',
    borderLeftWidth: 4,
  },
  quoteText: {
    fontSize: 16,
    lineHeight: 24,
    fontFamily: 'System',
  },
  quoteSource: {
    marginTop: 8,
    fontSize: 12,
    fontStyle: 'italic',
  },
});

export default QuoteBox;