# 📱 Instrucciones para Crear APK/AAB - Tzotzil Bible

## Prerrequisitos

1. **Cuenta de Expo/EAS**: Crea una cuenta gratuita en https://expo.dev/
2. **Google Play Console**: Cuenta de desarrollador ($25 USD una sola vez)
3. **EAS CLI instalado**: `npm install -g eas-cli`

## Proceso de Build

### 1. Autenticación
```bash
cd temp_nevin
eas login
```

### 2. Construir APK para Testing
```bash
eas build --platform android --profile preview
```
- **Tiempo estimado**: 10-15 minutos
- **Resultado**: APK instalable en cualquier dispositivo Android
- **Uso**: Testing local, distribución a testers

### 3. Construir AAB para Google Play Store
```bash
eas build --platform android --profile production
```
- **Tiempo estimado**: 10-15 minutos  
- **Resultado**: AAB optimizado para Google Play Store
- **Uso**: Subida oficial a Play Store

### 4. Descargar Archivos
- Ve a https://expo.dev/accounts/[tu-usuario]/projects/tzotzil-bible/builds
- Descarga tanto el APK como el AAB

## Subida a Google Play Store

### 1. Preparar Google Play Console
1. Ve a https://play.google.com/console
2. Crea nueva aplicación: "Tzotzil Bible"
3. Configura información básica:
   - **Nombre**: Tzotzil Bible
   - **Descripción**: Aplicación bilingüe de la Biblia (Español/Tzotzil) con asistente IA
   - **Categoría**: Libros y referencias
   - **Contenido**: Todas las edades

### 2. Subir AAB
1. Ve a "Producción" → "Crear nueva versión"
2. Sube el archivo `.aab`
3. Completa la información requerida:
   - Notas de la versión
   - Capturas de pantalla (mínimo 2)
   - Ícono de la aplicación

### 3. Configuración Obligatoria
- **Política de privacidad**: Requerida
- **Clasificación de contenido**: Completar cuestionario
- **Público objetivo**: Seleccionar edades apropiadas
- **Datos de seguridad**: Declarar qué datos recopila la app

### 4. Publicación
1. Revisar toda la información
2. Enviar para revisión (1-3 días típicamente)
3. Una vez aprobado, publicar

## Configuración del Proyecto

Tu proyecto ya tiene configurado:
- ✅ **Package ID**: `com.chyrris.tzotzilbible`
- ✅ **Version Code**: 22
- ✅ **EAS Project ID**: a810d3d6-839d-49b2-9dab-c42a44e3a6b0
- ✅ **Build Profiles**: Configurados para APK y AAB
- ✅ **Iconos y Splash Screen**: Listos

## Resolución de Problemas

### Error de Keystore
Si EAS pregunta sobre keystore, selecciona:
- "Generate new keystore" (primera vez)
- EAS manejará automáticamente la firma

### Error de Dependencias
Si hay conflictos, usa:
```bash
npm install --legacy-peer-deps
```

### Build Falla
- Revisa los logs en https://expo.dev/
- Verifica que todos los assets existan
- Asegúrate que no hay imports rotos

## Contacto y Soporte

- **Documentación EAS**: https://docs.expo.dev/build/
- **Google Play Console**: https://support.google.com/googleplay/android-developer/
- **Expo Community**: https://forums.expo.dev/

---

🎉 **¡Tu app Tzotzil Bible con Revolutionary Nevin AI v2.0 estará lista para el mundo!**