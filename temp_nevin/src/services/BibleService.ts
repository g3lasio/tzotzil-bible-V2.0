
import axios from 'axios';
import { API_URL } from '../config';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface BibleVerse {
  book: string;
  chapter: number;
  verse: number;
  tzotzil_text: string;
  spanish_text: string;
}

export class BibleService {
  static async getBooks(): Promise<string[]> {
    try {
      const cachedBooks = await AsyncStorage.getItem('bible_books');
      if (cachedBooks) {
        return JSON.parse(cachedBooks);
      }

      const response = await axios.get(`${API_URL}/api/bible/books`);
      await AsyncStorage.setItem('bible_books', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error('Error fetching books:', error);
      throw new Error('Error obteniendo libros');
    }
  }

  static async getChapters(book: string): Promise<number[]> {
    try {
      const cacheKey = `chapters_${book}`;
      const cachedChapters = await AsyncStorage.getItem(cacheKey);
      if (cachedChapters) {
        return JSON.parse(cachedChapters);
      }

      const response = await axios.get(`${API_URL}/api/bible/chapters/${book}`);
      await AsyncStorage.setItem(cacheKey, JSON.stringify(response.data.chapters));
      return response.data.chapters;
    } catch (error) {
      console.error('Error fetching chapters:', error);
      throw new Error('Error obteniendo capítulos');
    }
  }

  static async getVerses(book: string, chapter: number): Promise<BibleVerse[]> {
    try {
      const cacheKey = `verses_${book}_${chapter}`;
      const cachedVerses = await AsyncStorage.getItem(cacheKey);
      if (cachedVerses) {
        return JSON.parse(cachedVerses);
      }

      const response = await axios.get(`${API_URL}/api/bible/verses/${book}/${chapter}`);
      await AsyncStorage.setItem(cacheKey, JSON.stringify(response.data.verses));
      return response.data.verses;
    } catch (error) {
      console.error('Error fetching verses:', error);
      throw new Error('Error obteniendo versículos');
    }
  }

  static async clearCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const bibleKeys = keys.filter(key => 
        key.startsWith('bible_') || 
        key.startsWith('chapters_') || 
        key.startsWith('verses_')
      );
      await AsyncStorage.multiRemove(bibleKeys);
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }
}
