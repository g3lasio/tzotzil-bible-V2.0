#!/bin/bash
# Production deployment script for Flask app with gunicorn
# Dependencies are pre-installed via pyproject.toml in Nix environment

set -e

echo "=== INICIANDO DEPLOYMENT DE PRODUCCIÓN ==="

# Configurar puerto (Replit asigna automáticamente $PORT)
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
