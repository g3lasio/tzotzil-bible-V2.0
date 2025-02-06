
import * as SQLite from 'expo-sqlite';
import * as FileSystem from 'expo-file-system';
import { Asset } from 'expo-asset';
import { Platform } from 'react-native';
import { BibleVerse, Book, Chapter } from '../types/bible';

export class DatabaseService {
  private static instance: DatabaseService;
  private db: SQLite.SQLiteDatabase | null = null;
  private static readonly DB_NAME = 'bible.db';

  private constructor() {}

  static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  async initialize(): Promise<boolean> {
    try {
      await this.copyDatabaseFile();
      this.db = await SQLite.openDatabaseAsync(DatabaseService.DB_NAME);
      return true;
    } catch (error) {
      console.error('Error initializing database:', error);
      return false;
    }
  }

  private async copyDatabaseFile(): Promise<void> {
    if (Platform.OS === 'web') return;

    const dbPath = `${FileSystem.documentDirectory}SQLite/${DatabaseService.DB_NAME}`;
    const fileExists = await FileSystem.getInfoAsync(dbPath);

    if (!fileExists.exists) {
      try {
        // Asegurar que el directorio existe
        await FileSystem.makeDirectoryAsync(
          `${FileSystem.documentDirectory}SQLite`,
          { intermediates: true }
        );

        // Copiar desde assets
        const asset = await Asset.loadAsync(require('../../assets/bible.db'));
        if (asset[0]?.localUri) {
          await FileSystem.copyAsync({
            from: asset[0].localUri,
            to: dbPath
          });
        }
      } catch (error) {
        console.error('Error copying database:', error);
        throw error;
      }
    }
  }

  async getBooks(): Promise<Book[]> {
    try {
      const result = await this.db?.transactionAsync(async (tx) => {
        const resultSet = await tx.executeSqlAsync(
          'SELECT * FROM books ORDER BY book_number',
          []
        );
        return resultSet.rows;
      });
      return result || [];
    } catch (error) {
      console.error('Error getting books:', error);
      return [];
    }
  }

  async getChapters(bookId: number): Promise<Chapter[]> {
    try {
      const result = await this.db?.transactionAsync(async (tx) => {
        const resultSet = await tx.executeSqlAsync(
          'SELECT * FROM chapters WHERE book_id = ? ORDER BY chapter_number',
          [bookId]
        );
        return resultSet.rows;
      });
      return result || [];
    } catch (error) {
      console.error('Error getting chapters:', error);
      return [];
    }
  }

  async getVerses(bookId: number, chapterNumber: number): Promise<BibleVerse[]> {
    try {
      const result = await this.db?.transactionAsync(async (tx) => {
        const resultSet = await tx.executeSqlAsync(
          'SELECT * FROM verses WHERE book_id = ? AND chapter = ? ORDER BY verse',
          [bookId, chapterNumber]
        );
        return resultSet.rows;
      });
      return result || [];
    } catch (error) {
      console.error('Error getting verses:', error);
      return [];
    }
  }

  async searchVerses(query: string): Promise<BibleVerse[]> {
    try {
      const result = await this.db?.transactionAsync(async (tx) => {
        const resultSet = await tx.executeSqlAsync(
          `SELECT v.*, b.name as book_name 
           FROM verses v 
           JOIN books b ON v.book_id = b.id 
           WHERE v.text LIKE ? OR v.text_tzotzil LIKE ?
           LIMIT 100`,
          [`%${query}%`, `%${query}%`]
        );
        return resultSet.rows;
      });
      return result || [];
    } catch (error) {
      console.error('Error searching verses:', error);
      return [];
    }
  }

  async close(): Promise<void> {
    try {
      if (this.db) {
        await this.db.closeAsync();
        this.db = null;
      }
    } catch (error) {
      console.error('Error closing database:', error);
    }
  }
}

export const databaseService = DatabaseService.getInstance();
export default DatabaseService;
