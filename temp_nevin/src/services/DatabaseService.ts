
import * as FileSystem from 'expo-file-system';
import * as SQLite from 'expo-sqlite';
import { Asset } from 'expo-asset';

export class DatabaseService {
  private static instance: DatabaseService;
  private db: SQLite.WebSQLDatabase | null = null;

  private constructor() {}

  static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  async initDatabase() {
    try {
      await this.copyDatabaseFile();
      this.db = SQLite.openDatabase('bible.db');
      return true;
    } catch (error) {
      console.error('Error initializing database:', error);
      return false;
    }
  }

  private async copyDatabaseFile() {
    const dbPath = `${FileSystem.documentDirectory}SQLite/bible.db`;
    const dbExists = await FileSystem.getInfoAsync(dbPath);

    if (!dbExists.exists) {
      try {
        // Asegurarse que el directorio existe
        await FileSystem.makeDirectoryAsync(
          `${FileSystem.documentDirectory}SQLite`,
          { intermediates: true }
        );

        // Copiar desde assets
        const asset = Asset.fromModule(require('../assets/bible.db'));
        await asset.downloadAsync();
        
        if (asset.localUri) {
          await FileSystem.copyAsync({
            from: asset.localUri,
            to: dbPath
          });
        }
      } catch (error) {
        console.error('Error copying database:', error);
        throw error;
      }
    }
  }

  async getVerses(book: string, chapter: number): Promise<any[]> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      this.db.transaction(tx => {
        tx.executeSql(
          'SELECT * FROM verses WHERE book = ? AND chapter = ?',
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

  async searchVerses(query: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      this.db.transaction(tx => {
        tx.executeSql(
          'SELECT * FROM verses WHERE text LIKE ?',
          [`%${query}%`],
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

export const databaseService = DatabaseService.getInstance();
