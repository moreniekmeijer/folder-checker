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

(cd "$DIST_DIR" && zip -r "$APP_NAME.zip" "$APP_NAME.app")

echo "Done! Zip available at: $ZIP_FILE"
