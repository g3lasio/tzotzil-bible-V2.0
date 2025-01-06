
import { MD3LightTheme } from 'react-native-paper';

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#00f3ff',
    secondary: '#0066cc',
    background: '#0d1117',
    surface: '#090d13',
    text: '#e6f3ff',
    textSecondary: '#99ccff',
    accent: '#007fff',
    glow: '#00f3ff',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16
  }
};
