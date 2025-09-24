#!/bin/bash
set -euo pipefail

APP_NAME="FolderChecker"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
ZIP_FILE="$DIST_DIR/$APP_NAME.zip"

echo "Preparing environment..."

if [ -d ".venv" ]; then
  echo "Activating virtual environment (.venv)..."
  source .venv/bin/activate
elif [ -d "venv" ]; then
  echo "Activating virtual environment (venv)..."
  source venv/bin/activate
else
  echo "No virtual environment found, using system Python."
fi

if [ -f "requirements.txt" ]; then
  echo "Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
fi

echo "Building $APP_NAME..."

rm -rf build "$DIST_DIR"
mkdir -p "$DIST_DIR"

python3 setup.py py2app

if [ ! -d "$APP_BUNDLE" ]; then
  echo "Error: App bundle '$APP_BUNDLE' not found!"
  exit 1
fi

echo "Creating zip archive..."

TMP_DIR=$(mktemp -d)
cp -R "$APP_BUNDLE" "$TMP_DIR/"
cp README.md README_nl.md LICENSE "$TMP_DIR/" 2>/dev/null || true

(
  cd "$TMP_DIR"
  zip -r "$OLDPWD/$ZIP_FILE" ./*
)

rm -rf "$TMP_DIR"

echo "Done! App and zip are available in: $DIST_DIR"
