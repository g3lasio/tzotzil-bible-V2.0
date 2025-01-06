import AsyncStorage from '@react-native-async-storage/async-storage';

type CacheItem<T> = {
  data: T;
  timestamp: number;
  expiresIn: number;
};

class CacheService {
  private static instance: CacheService;
  private cachePrefix = '@nevin_cache:';
  private defaultExpiration = 7 * 24 * 60 * 60 * 1000; // 7 días

  private constructor() {}

  static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  async set<T>(key: string, data: T, expiresIn: number = this.defaultExpiration): Promise<void> {
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      expiresIn,
    };
    try {
      await AsyncStorage.setItem(
        this.cachePrefix + key,
        JSON.stringify(item)
      );
    } catch (error) {
      console.error('Error guardando en caché:', error);
    }
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      const item = await AsyncStorage.getItem(this.cachePrefix + key);
      if (!item) return null;

      const cacheItem: CacheItem<T> = JSON.parse(item);
      const now = Date.now();
      
      if (now - cacheItem.timestamp > cacheItem.expiresIn) {
        await this.remove(key);
        return null;
      }

      return cacheItem.data;
    } catch (error) {
      console.error('Error leyendo caché:', error);
      return null;
    }
  }

  async remove(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.cachePrefix + key);
    } catch (error) {
      console.error('Error eliminando caché:', error);
    }
  }

  async clear(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(this.cachePrefix));
      await AsyncStorage.multiRemove(cacheKeys);
    } catch (error) {
      console.error('Error limpiando caché:', error);
    }
  }
}

export const cacheService = CacheService.getInstance();
