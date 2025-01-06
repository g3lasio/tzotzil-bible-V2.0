
import * as SQLite from 'expo-sqlite';
import * as FileSystem from 'expo-file-system';

export class DatabaseService {
  private db: SQLite.SQLiteDatabase;

  constructor() {
    this.db = SQLite.openDatabaseSync('bible_app.db');
  }

  async initDatabase() {
    try {
      await this.setupTables();
      await this.copyDatabaseIfNeeded();
    } catch (error) {
      console.error('Error initializing database:', error);
      throw error;
    }
  }

  private async setupTables() {
    const queries = [
      `CREATE TABLE IF NOT EXISTS bible_verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book TEXT,
        chapter INTEGER,
        verse INTEGER,
        tzotzil_text TEXT,
        spanish_text TEXT
      )`,
      `CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        book TEXT,
        chapter INTEGER,
        verse INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )`
    ];

    for (const query of queries) {
      await this.executeQuery(query);
    }
  }

  private async copyDatabaseIfNeeded() {
    const dbPath = `${FileSystem.documentDirectory}SQLite/bible_app.db`;
    const fileInfo = await FileSystem.getInfoAsync(dbPath);
    
    if (!fileInfo.exists) {
      // Use API instead of local database
      return await BibleService.getVerses(book, chapter);
      
      const dbFolder = `${FileSystem.documentDirectory}SQLite`;
      await FileSystem.makeDirectoryAsync(dbFolder, { intermediates: true });
      
      await FileSystem.copyAsync({
        from: asset.localUri || '',
        to: dbPath
      });
    }
  }

  async executeQuery(query: string, params: any[] = []): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(query, params,
          (_, result) => resolve(result),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }

  async getVerses(book: string, chapter?: number) {
    const query = chapter 
      ? `SELECT * FROM bible_verses WHERE book = ? AND chapter = ?`
      : `SELECT * FROM bible_verses WHERE book = ?`;
    const params = chapter ? [book, chapter] : [book];
    
    const result = await this.executeQuery(query, params);
    return result.rows._array;
  }
}

export const databaseService = new DatabaseService();
