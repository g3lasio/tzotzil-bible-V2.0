import * as SQLite from 'expo-sqlite';
import * as FileSystem from 'expo-file-system';

export class DatabaseService {
  private db: SQLite.WebSQLDatabase;

  constructor() {
    this.db = SQLite.openDatabase('bible.db');
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    try {
      const dbExists = await this.checkIfDatabaseExists();
      if (!dbExists) {
        await this.copyInitialDatabase();
      }
    } catch (error) {
      console.error('Database initialization error:', error);
    }
  }

  private async checkIfDatabaseExists() {
    const dbPath = `${FileSystem.documentDirectory}SQLite/bible.db`;
    return await FileSystem.getInfoAsync(dbPath);
  }

  private async copyInitialDatabase() {
    const dbAsset = require('../../assets/bible.db');
    const dbPath = `${FileSystem.documentDirectory}SQLite/bible.db`;
    await FileSystem.makeDirectoryAsync(
      `${FileSystem.documentDirectory}SQLite`,
      { intermediates: true }
    );
    await FileSystem.downloadAsync(dbAsset, dbPath);
  }
}