import os
import shutil
import subprocess
from logger_setup import logger
from dialogs import show_dialog
from AppKit import NSBundle, NSApp


def remove_from_login_items(app_path):
    if not os.path.exists(app_path):
        logger.info(f"App bundle path no longer exists, trying to remove login item by name…")
    app_name = os.path.splitext(os.path.basename(app_path))[0]

    script = f'''
    tell application "System Events"
        if exists login item "{app_name}" then
            delete login item "{app_name}"
        end if
    end tell
    '''
    try:
        subprocess.run(['osascript', '-e', script], check=True)
        logger.info(f"Removed from Login Items: {app_name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Could not remove from Login Items: {e}")


def uninstall_app():
    choice = show_dialog(
        "Uninstall Folder Checker?\n\nThis will remove all app data and quit the app.",
        icon_name="sweeper",
        buttons=("Cancel", "Uninstall"),
        default_button="Cancel",
        timeout=60,
    )

    if choice != "Uninstall":
        logger.info("Uninstall cancelled by user.")
        return

    app_support = os.path.expanduser("~/Library/Application Support/FolderChecker")
    log_dir = os.path.expanduser("~/Library/Logs/FolderChecker")
    bundle = NSBundle.mainBundle()
    app_bundle_path = bundle.bundlePath()

    for path in (app_support, log_dir):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                logger.info(f"Removed {path}")
            except Exception as e:
                logger.error(f"Error removing {path}: {e}")

    remove_from_login_items(app_bundle_path)

    if os.path.exists(app_bundle_path):
        try:
            shutil.rmtree(app_bundle_path)
            logger.info(f"Removed app bundle: {app_bundle_path}")
        except Exception as e:
            logger.error(f"Error removing app bundle: {e}")

    NSApp.terminate_(None)
