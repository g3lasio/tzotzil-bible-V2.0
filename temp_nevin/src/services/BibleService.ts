import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { API_URL } from '../config';

// Assumed CacheService implementation (needs to be defined elsewhere)
class CacheService {
  static async getCachedVerses(book: string, chapter: number): Promise<any[]> {
    try {
      const cachedData = await AsyncStorage.getItem(`verses_${book}_${chapter}`);
      return cachedData ? JSON.parse(cachedData) : [];
    } catch (error) {
      console.error('Error getting cached verses:', error);
      return [];
    }
  }

  static async updateCache(verses: any[]): Promise<void> {
    try {
      const book = verses[0].book; // Assuming verses array is not empty and has book property
      const chapter = verses[0].chapter; // Assuming verses array is not empty and has chapter property
      await AsyncStorage.setItem(`verses_${book}_${chapter}`, JSON.stringify(verses));
    } catch (error) {
      console.error('Error updating cache:', error);
    }
  }
}


export class BibleService {
  static async getBooks() {
    try {
      const response = await axios.get(`${API_URL}/api/bible/books`);
      return response.data;
    } catch (error) {
      console.error('Error obteniendo libros:', error);
      throw error;
    }
  }

  static async getChapters(book: string) {
    try {
      const response = await axios.get(`${API_URL}/api/bible/chapters/${book}`);
      return response.data;
    } catch (error) {
      console.error('Error obteniendo capítulos:', error);
      throw error;
    }
  }

  static async getVerses(book: string, chapter: number): Promise<any[]> {
    try {
      // Intentar obtener del caché primero
      const cachedVerses = await CacheService.getCachedVerses(book, chapter);
      if (cachedVerses.length > 0) {
        return cachedVerses;
      }

      // Si no está en caché, obtener de la API
      const response = await axios.get(`${API_URL}/chapter/${book}/${chapter}`);
      const verses = response.data;

      // Actualizar caché
      await CacheService.updateCache(verses);
      return verses;
    } catch (error) {
      console.error('Error fetching verses:', error);
      return [];
    }
  }

  static async getFavoriteVerses() {
    try {
      const favorites = await AsyncStorage.getItem('favorite_verses');
      return favorites ? JSON.parse(favorites) : [];
    } catch (error) {
      console.error('Error obteniendo versículos favoritos:', error);
      return [];
    }
  }

  static async addFavoriteVerse(verse: any) {
    try {
      const favorites = await this.getFavoriteVerses();
      const updatedFavorites = [...favorites, verse];
      await AsyncStorage.setItem('favorite_verses', JSON.stringify(updatedFavorites));
    } catch (error) {
      console.error('Error guardando versículo favorito:', error);
    }
  }
}