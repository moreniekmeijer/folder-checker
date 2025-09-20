#!/bin/bash
set -e

# Configuratie
APP_NAME="FolderChecker"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
DMG_NAME="$DIST_DIR/$APP_NAME.dmg"

# Achtergrondafbeelding (PNG van ± 600x400px, bv. resources/dmg_background.png)
BACKGROUND_IMG="resources/dmg_background.png"

# 1. Oude build en DMG opruimen
echo "Cleaning old build and DMG..."
rm -rf build "$DIST_DIR"
mkdir -p "$DIST_DIR"

# 2. App bouwen met py2app
echo "Building .app bundle with py2app..."
python3 setup.py py2app

# 3. Controleren of de .app bestaat
if [ ! -d "$APP_BUNDLE" ]; then
  echo "Error: App bundle '$APP_BUNDLE' not found!"
  exit 1
fi

# 4. DMG content map aanmaken
DMG_CONTENT="$DIST_DIR/dmgcontent"
mkdir -p "$DMG_CONTENT"
cp -R "$APP_BUNDLE" "$DMG_CONTENT"
ln -s /Applications "$DMG_CONTENT/Applications"

# 5. Tijdelijke DMG maken
TMP_DMG="$DIST_DIR/tmp.dmg"
hdiutil create -volname "$APP_NAME" \
  -srcfolder "$DMG_CONTENT" \
  -ov -format UDRW "$TMP_DMG"

# 6. DMG mounten
MOUNT_POINT=$(hdiutil attach -readwrite -noverify -noautoopen "$TMP_DMG" | grep Volumes | awk '{print $3}')

# 7. Achtergrondmap maken
mkdir -p "$MOUNT_POINT/.background"
cp "$BACKGROUND_IMG" "$MOUNT_POINT/.background/background.png"

# 8. Finder venster layout instellen met AppleScript
osascript <<EOD
tell application "Finder"
  tell disk "$APP_NAME"
    open
    set current view of container window to icon view
    set toolbar visible of container window to false
    set statusbar visible of container window to false
    set the bounds of container window to {100, 100, 700, 500}
    set viewOptions to the icon view options of container window
    set arrangement of viewOptions to not arranged
    set icon size of viewOptions to 128
    set background picture of viewOptions to file ".background:background.png"
    -- Iconen positioneren
    set position of item "$APP_NAME.app" of container window to {150, 200}
    set position of item "Applications" of container window to {450, 200}
    update without registering applications
    delay 2
    close
    open
    update without registering applications
    delay 2
  end tell
end tell
EOD

# 9. Unmount
hdiutil detach "$MOUNT_POINT"

# 10. Comprimeren naar uiteindelijke read-only DMG
hdiutil convert "$TMP_DMG" -format UDZO -o "$DMG_NAME"

# 11. Opruimen
rm -rf "$TMP_DMG" "$DMG_CONTENT"

echo "Done!"
echo "DMG available at: $DMG_NAME"
