
import AsyncStorage from '@react-native-async-storage/async-storage';

export class VerseService {
  static async handleHighlight(verseId: string, color: string) {
    try {
      const highlights = await AsyncStorage.getItem('verse_highlights') || '{}';
      const highlightData = JSON.parse(highlights);
      highlightData[verseId] = color;
      await AsyncStorage.setItem('verse_highlights', JSON.stringify(highlightData));
      return true;
    } catch (error) {
      console.error('Error highlighting verse:', error);
      return false;
    }
  }

  static async shareVerse(verseId: string, verseText: string, reference: string) {
    try {
      const shareText = `${reference}\n\n${verseText}\n\nCompartido desde Biblia Tzotzil`;
      return shareText;
    } catch (error) {
      console.error('Error sharing verse:', error);
      throw error;
    }
  }
}
