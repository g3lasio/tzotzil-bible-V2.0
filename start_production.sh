#!/bin/bash
# Production deployment script for Flask app with gunicorn

set -e

echo "=== INICIANDO DEPLOYMENT DE PRODUCCIÓN ==="

# Actualizar pip y limpiar caché
echo "📦 Instalando dependencias..."
pip install -U pip --quiet
pip install --no-cache-dir -r requirements.txt --quiet

# Verificar que gunicorn está instalado
if ! command -v gunicorn &> /dev/null; then
    echo "❌ ERROR: gunicorn no está instalado"
    pip install gunicorn
fi

echo "✅ Dependencias instaladas"

# Configurar puerto
export PORT=${PORT:-5000}

echo "🚀 Iniciando aplicación Flask con gunicorn en 0.0.0.0:$PORT"
echo "Workers: 2, Thread workers"

# Iniciar gunicorn con factory pattern
exec gunicorn 'app:create_app()' \
    --workers 2 \
    --worker-class gthread \
    --threads 2 \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level info
