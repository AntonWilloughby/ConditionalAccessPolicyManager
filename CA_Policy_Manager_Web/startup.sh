#!/bin/bash
# Azure App Service startup script

echo "Starting CA Policy Manager..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create upload directory if needed
mkdir -p $UPLOAD_FOLDER

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 --access-logfile '-' --error-logfile '-' app:app
