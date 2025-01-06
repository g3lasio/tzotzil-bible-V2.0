
import * as SQLite from 'expo-sqlite';
import * as FileSystem from 'expo-file-system';

export class CacheService {
  private static db = SQLite.openDatabase('bible_cache.db');

  static async initializeCache() {
    try {
      await this.db.transaction(tx => {
        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS verses_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            tzotzil_text TEXT,
            spanish_text TEXT,
            last_updated INTEGER
          )`
        );
      });
    } catch (error) {
      console.error('Error initializing cache:', error);
    }
  }

  static async updateCache(verses: any[]) {
    try {
      await this.db.transaction(tx => {
        verses.forEach(verse => {
          tx.executeSql(
            `INSERT OR REPLACE INTO verses_cache 
            (book, chapter, verse, tzotzil_text, spanish_text, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)`,
            [verse.book, verse.chapter, verse.verse, verse.tzotzil_text, 
             verse.spanish_text, Date.now()]
          );
        });
      });
    } catch (error) {
      console.error('Error updating cache:', error);
    }
  }

  static async getCachedVerses(book: string, chapter: number): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(
          `SELECT * FROM verses_cache 
           WHERE book = ? AND chapter = ?
           ORDER BY verse`,
          [book, chapter],
          (_, { rows: { _array } }) => resolve(_array),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }
}
