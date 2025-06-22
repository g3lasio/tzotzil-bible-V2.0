# Google Play Compliance Guide - Tzotzil Bible

## Problema Resuelto
Google Play rechazó la versión anterior debido a:
1. Package ID inconsistente (`com.g3lasio.TzotzilBible` vs `com.chyrris.tzotzilbible`)
2. Imágenes con nombres aleatorios que violan políticas de contenido
3. Configuración de metadatos incompleta

## Cambios Implementados

### 1. Limpieza de Assets
- Eliminadas todas las imágenes con nombres aleatorios (`image_*.png`)
- Removidas imágenes de WhatsApp que pueden contener metadatos problemáticos
- Mantenidos solo assets oficiales necesarios para la app

### 2. Configuración Corregida
- **Package ID unificado**: `com.chyrris.tzotzilbible`
- **Nombre consistente**: "Tzotzil Bible - Nevin AI"
- **Versión actualizada**: 2.1.0 (versionCode: 21)
- **Target SDK**: 34 (Android 14)
- **Permisos**: Lista vacía (sin permisos innecesarios)

### 3. Metadatos de Play Store
- Descripción clara del propósito religioso/educativo
- Categoría: Educación o Libros y Referencias
- Clasificación de contenido: Para todas las edades
- Sin anuncios ni compras in-app

## Recomendaciones para Nueva Submisión

### Assets Requeridos
1. **Icono**: 512x512px, formato PNG
2. **Screenshots**: Al menos 2 por orientación
3. **Feature Graphic**: 1024x500px
4. **Descripción detallada** en español e inglés

### Descripción Sugerida
```
"Tzotzil Bible es una aplicación educativa que proporciona acceso a textos bíblicos en español y tzotzil. Incluye a Nevin, un asistente de IA para interpretación bíblica y orientación espiritual. 

Características:
- Texto bíblico bilingüe (Español/Tzotzil)
- Búsqueda avanzada de versículos
- Asistente de IA para consultas bíblicas
- Interfaz fácil de usar
- Contenido apropiado para todas las edades

Esta aplicación está diseñada para la comunidad tzotzil y estudiosos de la Biblia que buscan acceso a textos sagrados en su idioma nativo."
```

### Categorías Recomendadas
- Principal: Educación
- Secundaria: Libros y Referencias

### Cumplimiento de Políticas
- ✅ Contenido religioso educativo (permitido)
- ✅ Sin contenido sensible o controvertido
- ✅ Sin recopilación de datos personales
- ✅ Sin publicidad
- ✅ Código limpio sin vulnerabilidades

## Próximos Pasos
1. Generar nuevo APK/AAB con la configuración corregida
2. Crear assets de Play Store profesionales
3. Escribir descripción detallada
4. Subir como nueva versión (no actualización)
5. Seleccionar categorías apropiadas
6. Completar cuestionario de clasificación de contenido