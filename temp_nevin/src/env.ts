export const ENV = {
  API_URL: process.env.API_URL || 'http://localhost:5000',
  OPENAI_API_KEY: process.env.OPENAI_API_KEY,
};

export type ENV = typeof ENV;

// Asegurar que las variables de entorno estén definidas
Object.entries(ENV).forEach(([key, value]) => {
  if (value === undefined) {
    console.warn(`La variable de entorno ${key} no está definida`);
  }
});
