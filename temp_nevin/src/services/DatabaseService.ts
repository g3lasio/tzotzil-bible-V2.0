
import * as SQLite from 'expo-sqlite';
import { Asset } from 'expo-asset';
import * as FileSystem from 'expo-file-system';

class DatabaseService {
  private db: SQLite.WebSQLDatabase;

  constructor() {
    this.db = SQLite.openDatabase('bible_app.db');
  }

  async initDatabase() {
    try {
      const exists = await this.checkIfDatabaseExists();
      if (!exists) {
        await this.copyDatabase();
      }
      await this.setupTables();
    } catch (error) {
      console.error('Error inicializando base de datos:', error);
      throw error;
    }
  }

  private async checkIfDatabaseExists() {
    const dbPath = `${FileSystem.documentDirectory}SQLite/bible_app.db`;
    const fileInfo = await FileSystem.getInfoAsync(dbPath);
    return fileInfo.exists;
  }

  private async copyDatabase() {
    try {
      const dbAsset = require('../../assets/bible_app.db');
      const asset = Asset.fromModule(dbAsset);
      await asset.downloadAsync();
      
      const dbFolder = `${FileSystem.documentDirectory}SQLite`;
      const folderInfo = await FileSystem.getInfoAsync(dbFolder);
      if (!folderInfo.exists) {
        await FileSystem.makeDirectoryAsync(dbFolder, { intermediates: true });
      }
      
      await FileSystem.copyAsync({
        from: asset.localUri || '',
        to: `${dbFolder}/bible_app.db`
      });
    } catch (error) {
      console.error('Error copiando base de datos:', error);
      throw error;
    }
  }

  private async setupTables() {
    const queries = [
      `CREATE TABLE IF NOT EXISTS user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        font_size INTEGER,
        theme TEXT,
        language TEXT
      );`,
      `CREATE TABLE IF NOT EXISTS favorite_verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        book TEXT,
        chapter INTEGER,
        verse INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      );`
    ];

    for (const query of queries) {
      await this.executeQuery(query);
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
}

export const databaseService = new DatabaseService();
