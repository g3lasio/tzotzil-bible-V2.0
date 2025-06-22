#!/bin/bash
# Deployment script for Flask application
echo "Starting Flask application deployment..."

# Set environment variables for production
export FLASK_ENV=production
export PORT=5000

# Clean up any existing processes on port 5000
pkill -f "python main.py" || true
sleep 2

# Start the Flask application
echo "Starting Flask server on port 5000..."
python main.py