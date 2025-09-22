#!/bin/bash
set -euo pipefail

APP_NAME="FolderChecker"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
ZIP_FILE="$DIST_DIR/$APP_NAME.zip"

echo "Zipping $APP_NAME..."

if [ ! -d "$APP_BUNDLE" ]; then
  echo "Error: App bundle '$APP_BUNDLE' not found!"
  exit 1
fi

TMP_DIR=$(mktemp -d)
cp -R "$APP_BUNDLE" "$TMP_DIR/"
cp README.md README_nl.md LICENSE "$TMP_DIR/" || true

(
  cd "$TMP_DIR"
  zip -r "$ZIP_FILE" ./*
)

rm -rf "$TMP_DIR"

echo "Done! Zip available at: $ZIP_FILE"
