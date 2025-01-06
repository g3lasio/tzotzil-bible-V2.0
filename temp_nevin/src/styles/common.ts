
import { StyleSheet } from 'react-native';
import { theme } from '../theme';

export const commonStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: 16,
  },
  card: {
    marginBottom: 12,
    borderRadius: 8,
    elevation: 2,
    backgroundColor: 'white',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    color: theme.colors.primary,
  },
  text: {
    fontSize: 16,
    color: theme.colors.onSurface,
    marginBottom: 8,
  },
  button: {
    marginVertical: 8,
    borderRadius: 8,
  },
  input: {
    marginBottom: 16,
    backgroundColor: 'white',
  }
});
