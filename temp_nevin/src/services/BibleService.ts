
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { API_URL } from '../config';

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

  static async getVerses(book: string, chapter: number) {
    try {
      const response = await axios.get(`${API_URL}/api/bible/verses/${book}/${chapter}`);
      return response.data;
    } catch (error) {
      console.error('Error obteniendo versículos:', error);
      throw error;
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
