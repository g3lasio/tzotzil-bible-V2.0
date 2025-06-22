# Instrucciones para Generar APK - Tzotzil Bible

## Configuración Lista
✅ **Nombre**: Tzotzil Bible  
✅ **Package ID**: com.chyrris.tzotzilbible  
✅ **Versión**: 2.1.0 (versionCode: 21)  
✅ **Assets**: Iconos válidos instalados  
✅ **Configuración**: Google Play compliance implementada  

## Método 1: EAS Build (Recomendado)

### Prerrequisitos
```bash
npm install -g eas-cli
eas login
# Usa tu cuenta de Expo
```

### Pasos
```bash
cd temp_nevin
eas build --platform android --profile preview
```

Esto generará un APK que puedes descargar desde la consola de Expo.

## Método 2: Build Local con Android Studio

### Prerrequisitos
- Android Studio instalado
- Android SDK configurado
- Java JDK 11+ instalado

### Pasos
```bash
cd temp_nevin
npm install
npx expo run:android --variant release
```

## Método 3: Prebuild + Gradle

### Pasos
```bash
cd temp_nevin
npm install
npx expo prebuild --platform android
cd android
./gradlew assembleRelease
```

El APK estará en: `android/app/build/outputs/apk/release/app-release.apk`

## Verificación Final

Antes de subir a Google Play, verifica:
- [ ] Package ID: com.chyrris.tzotzilbible
- [ ] Nombre: Tzotzil Bible
- [ ] Versión: 2.1.0
- [ ] Sin imágenes problemáticas
- [ ] Configuración de permisos limpia

## Play Store Submission

1. **Categorías**: Educación > Libros y Referencias
2. **Descripción**: Usa la del archivo GOOGLE_PLAY_COMPLIANCE.md
3. **Clasificación**: Para todas las edades
4. **Screenshots**: Incluye capturas de la interfaz bíblica y Nevin AI

## Archivos de Configuración Actualizados
- `app.json`: Configuración completa
- `eas.json`: Perfiles de build
- `GOOGLE_PLAY_COMPLIANCE.md`: Guía de cumplimiento

## Si Encuentras Problemas

1. **Error de autenticación EAS**: Ejecuta `eas login`
2. **Error de Android SDK**: Verifica ANDROID_HOME
3. **Error de Java**: Usa JDK 11 o 17
4. **Error de memoria**: Añade `--max-old-space-size=8192` a node

El proyecto está completamente preparado para generar el APK con la configuración correcta para Google Play.