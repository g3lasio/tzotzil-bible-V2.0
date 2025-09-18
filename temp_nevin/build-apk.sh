#!/bin/bash

echo "🚀 Script de Build Automatizado - Tzotzil Bible APK/AAB"
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "app.json" ]; then
    echo "❌ Error: No se encontró app.json. Ejecuta este script desde el directorio temp_nevin"
    exit 1
fi

# Verificar que EAS CLI está instalado
if ! command -v eas &> /dev/null; then
    echo "📦 Instalando EAS CLI..."
    npm install -g eas-cli
fi

echo "✅ EAS CLI encontrado"

# Verificar autenticación
echo "🔐 Verificando autenticación con Expo..."
if ! eas whoami &> /dev/null; then
    echo "❌ No estás autenticado. Ejecutando login..."
    eas login
fi

echo "✅ Autenticación verificada"

# Mostrar información del proyecto
echo "📱 Información del Proyecto:"
echo "   Nombre: $(grep '"name"' app.json | head -1 | cut -d'"' -f4)"
echo "   Versión: $(grep '"version"' app.json | head -1 | cut -d'"' -f4)"
echo "   Package ID: $(grep '"package"' app.json | cut -d'"' -f4)"

echo ""
echo "¿Qué tipo de build quieres crear?"
echo "1) APK (para testing)"
echo "2) AAB (para Google Play Store)"
echo "3) Ambos"
read -p "Selecciona una opción (1-3): " BUILD_OPTION

case $BUILD_OPTION in
    1)
        echo "🔨 Construyendo APK..."
        eas build --platform android --profile preview
        ;;
    2)
        echo "🔨 Construyendo AAB..."
        eas build --platform android --profile production
        ;;
    3)
        echo "🔨 Construyendo APK primero..."
        eas build --platform android --profile preview
        echo "🔨 Construyendo AAB..."
        eas build --platform android --profile production
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ Build completado!"
echo "📁 Ve a https://expo.dev/accounts/$(eas whoami 2>/dev/null)/projects/tzotzil-bible/builds para descargar"
echo ""
echo "📋 Próximos pasos:"
echo "1. Descarga el archivo AAB desde el dashboard de Expo"
echo "2. Ve a Google Play Console: https://play.google.com/console"
echo "3. Crea una nueva app o ve a una existente"
echo "4. Sube el archivo AAB en la sección de 'Producción'"
echo "5. Completa la información requerida y publica"
echo ""
echo "🎉 ¡Tu app Tzotzil Bible estará pronto en Google Play Store!"