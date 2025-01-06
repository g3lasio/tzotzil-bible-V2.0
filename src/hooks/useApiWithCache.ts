import { useState, useEffect } from 'react';
import { cacheService } from '../services/cacheService';
import { BIBLE_API_URL } from '@env';

interface UseApiWithCacheOptions {
  endpoint: string;
  cacheKey?: string;
  expiresIn?: number;
  enabled?: boolean;
}

export function useApiWithCache<T>(options: UseApiWithCacheOptions) {
  const { endpoint, cacheKey = endpoint, expiresIn, enabled = true } = options;
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
        // Intentar obtener datos del caché primero
        const cachedData = await cacheService.get<T>(cacheKey);
        if (cachedData) {
          if (isMounted) {
            setData(cachedData);
            setLoading(false);
          }
          return;
        }

        // Si no hay caché, hacer la petición a la API
        const response = await fetch(`${BIBLE_API_URL}${endpoint}`);
        if (!response.ok) {
          throw new Error('Error en la petición');
        }

        const result = await response.json();
        if (isMounted) {
          setData(result);
          // Guardar en caché
          await cacheService.set(cacheKey, result, expiresIn);
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
