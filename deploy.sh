#!/bin/bash

# Exit on error
set -e

# Hardcoded VPS details
VPS_IP="217.114.4.101"
USER="root"
PASSWORD="Ag0384802#"

# Remote directories
REMOTE_JS_DIR="/var/www/kfc-frontend/static/js/"
REMOTE_CSS_DIR="/var/www/kfc-frontend/static/css/"
REMOTE_HTML_DIR="/var/www/kfc-frontend"
REMOTE_APP_DIR="/var/www/kfc-backend/"
REMOTE_IMG_DIR="/var/www/kfc-frontend/images/"


# Local build directory
BUILD_DIR="./build"
# APP_FILES=("./backend/new/app.py") # Files to be deployed to the backend
APP_DIR="./backend/new"
APP_FILES=(
  "$APP_DIR/app.py"
  "$APP_DIR/routes"
  "$APP_DIR/middleware"
  "$APP_DIR/utils"
)
# Ensure dependencies are installed and build the project
echo "Building the frontend..."
npm install --legacy-peer-deps
npm run build

# Clean remote frontend directories
echo "Cleaning remote frontend directories..."
sshpass -p "$PASSWORD" ssh $USER@$VPS_IP "rm -rf $REMOTE_JS_DIR* $REMOTE_CSS_DIR*"

# Upload frontend files
echo "Uploading frontend files to VPS..."

# Upload JS files
sshpass -p "$PASSWORD" scp -r $BUILD_DIR/static/js/* $USER@$VPS_IP:$REMOTE_JS_DIR

# Upload CSS files
sshpass -p "$PASSWORD" scp -r $BUILD_DIR/static/css/* $USER@$VPS_IP:$REMOTE_CSS_DIR

# Upload HTML files
sshpass -p "$PASSWORD" scp -r $BUILD_DIR/*.html $USER@$VPS_IP:$REMOTE_HTML_DIR

sshpass -p "$PASSWORD" scp -r $BUILD_DIR/images $USER@$VPS_IP:$REMOTE_IMG_DIR


# Deploy backend files
echo "Deploying backend files to VPS..."
sshpass -p "$PASSWORD" ssh $USER@$VPS_IP "mkdir -p $REMOTE_APP_DIR"

# Upload all backend files and folders
for FILE in "${APP_FILES[@]}"; do
    sshpass -p "$PASSWORD" scp -r "$FILE" $USER@$VPS_IP:$REMOTE_APP_DIR
done
# Restart backend services if necessary (optional)
# echo "Restarting backend services..."
# sshpass -p "$PASSWORD" ssh $USER@$VPS_IP "systemctl restart your-backend-service"

echo "Deployment completed successfully."
