import { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface UseApiWithCacheOptions {
  endpoint: string;
  cacheKey?: string;
  expiresIn?: number; // tiempo en minutos
  enabled?: boolean;
}

export function useApiWithCache<T>(options: UseApiWithCacheOptions) {
  const { endpoint, cacheKey = endpoint, expiresIn = 30, enabled = true } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      if (!enabled) {
        setLoading(false);
        return;
      }

      try {
        // Intentar obtener datos del caché
        const cached = await AsyncStorage.getItem(`api_cache_${cacheKey}`);
        if (cached) {
          const { data: cachedData, timestamp } = JSON.parse(cached);
          const isExpired = Date.now() - timestamp > expiresIn * 60 * 1000;

          if (!isExpired) {
            if (isMounted) {
              setData(cachedData);
              setLoading(false);
            }
            return;
          }
        }

        // Si no hay caché o expiró, hacer la petición
        const response = await api.get<T>(endpoint);
        if (isMounted) {
          setData(response.data);
          // Guardar en caché
          await AsyncStorage.setItem(`api_cache_${cacheKey}`, JSON.stringify({
            data: response.data,
            timestamp: Date.now()
          }));
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Error desconocido');
          console.error('Error fetching data:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [endpoint, cacheKey, expiresIn, enabled]);

  return { data, loading, error };
}
