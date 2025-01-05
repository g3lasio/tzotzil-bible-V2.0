
# Tzotzil Bible App

Una aplicación web moderna para acceder a la Biblia en español y tzotzil, con funcionalidades avanzadas de búsqueda e IA.

## 🌟 Características Principales

### Funcionalidades Básicas
- Lectura bilingüe (Español/Tzotzil)
- Navegación por libros y capítulos
- Búsqueda avanzada de versículos
- Modo offline con descarga de base de datos
- Sistema de promesas bíblicas aleatorias

### Nevin AI
- Asistente bíblico inteligente
- Base de conocimiento teológico extensa
- Interpretación contextual de escrituras
- Integración con OpenAI para análisis profundo

### Sistema de Usuarios
- Autenticación segura
- Perfiles de usuario personalizados
- Control de acceso basado en roles
- Gestión de suscripciones premium

## 🛠 Tecnologías Utilizadas

- **Backend**: Python/Flask
- **Base de Datos**: PostgreSQL (Neon.tech)
- **Frontend**: HTML5, CSS3, JavaScript
- **IA**: OpenAI GPT-4, FAISS para búsqueda vectorial
- **Cache**: Redis
- **Autenticación**: JWT

## 📦 Estructura del Proyecto

```
├── Nevin_AI/            # Motor de IA y procesamiento
├── static/              # Recursos estáticos
├── templates/           # Plantillas HTML
├── migrations/          # Migraciones de base de datos
└── instance/           # Configuración de instancia
```

## 🚀 Características de Implementación

### Modo Offline
- Descarga completa de la base de datos bíblica
- Caché local de recursos esenciales
- Sincronización automática cuando hay conexión

### Seguridad
- Encriptación de datos sensibles
- Protección contra inyección SQL
- Validación de entrada robusta
- Manejo seguro de sesiones

### Optimización
- Caché de consultas frecuentes
- Indexación eficiente de textos
- Compresión de recursos estáticos
- Lazy loading de contenido

## 🔧 Configuración del Proyecto

1. Configuración de variables de entorno:
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-api-key
```

2. Inicialización de la base de datos:
```bash
flask db upgrade
python import_bible_data.py
```

## 🌐 Despliegue

El proyecto está optimizado para despliegue en Replit:
1. Usar Replit Deployments
2. Configurar variables de entorno en Secrets
3. Habilitar Always On

## 📝 Estado del Proyecto

### Completado
- Sistema base de lectura bíblica
- Integración de Nevin AI
- Sistema de autenticación
- Modo offline básico

### En Desarrollo
- Mejoras en el sistema de búsqueda
- Optimización del modo offline
- Expansión de la base de conocimiento de Nevin
- Sistema de notas personales

### Próximas Características
- Grupos de estudio
- Compartir notas
- Modo de estudio avanzado
- Estadísticas de lectura

## 🤝 Contribución

Proyecto desarrollado y mantenido por DevWolf. Para contribuir:
1. Reportar bugs
2. Sugerir mejoras
3. Enviar pull requests

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.
