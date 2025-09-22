import os
import shutil
import subprocess
import AppKit
from logger_setup import logger


def remove_from_login_items(app_path):
    """Verwijdert de app uit macOS Login Items."""
    if not os.path.exists(app_path):
        logger.info(f"App bundle path no longer exists, trying to remove login item by name…")
    app_name = os.path.basename(app_path)

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
    alert = AppKit.NSAlert.alloc().init()
    alert.setMessageText_("Uninstall Folder Checker?")
    alert.setInformativeText_("This will remove all app data from the user and quit the app.")
    alert.addButtonWithTitle_("Uninstall")
    alert.addButtonWithTitle_("Cancel")
    alert.setAlertStyle_(AppKit.NSAlertStyleWarning)

    # --- custom icon ---
    bundle = AppKit.NSBundle.mainBundle()
    icon_path = bundle.pathForResource_ofType_("sweeper", "icns")
    if icon_path:
        img = AppKit.NSImage.alloc().initWithContentsOfFile_(icon_path)
        if img:
            img.setSize_((32, 32))
            img.setTemplate_(True)
            alert.setIcon_(img)

    response = alert.runModal()
    if response == AppKit.NSAlertFirstButtonReturn:
        app_support = os.path.expanduser("~/Library/Application Support/FolderChecker")
        if os.path.exists(app_support):
            try:
                shutil.rmtree(app_support)
                logger.info(f"Removed {app_support}")
            except Exception as e:
                logger.error(f"Error removing support folder: {e}")

        # launchagent = os.path.expanduser("~/Library/LaunchAgents/nl.moreniekmeijer.folderchecker.plist")
        # if os.path.exists(launchagent):
        #     try:
        #         subprocess.run(["launchctl", "unload", launchagent], capture_output=True)
        #         os.remove(launchagent)
        #         logger.info(f"Removed {launchagent}")
        #     except Exception as e:
        #         logger.error(f"Error removing launchagent: {e}")

        app_bundle_path = bundle.bundlePath()
        if os.path.exists(app_bundle_path):
            try:
                shutil.rmtree(app_bundle_path)
                logger.info(f"Removed {app_bundle_path}")
            except Exception as e:
                logger.error(f"Error removing app bundle: {e}")

        app_bundle_path = bundle.bundlePath()
        remove_from_login_items(app_bundle_path)

        log_dir = os.path.expanduser("~/Library/Logs/FolderChecker")
        if os.path.exists(log_dir):
            try:
                shutil.rmtree(log_dir)
                logger.info(f"Removed log directory {log_dir}")
            except Exception as e:
                logger.error(f"Error removing log directory: {e}")

        success = AppKit.NSAlert.alloc().init()
        success.setMessageText_("FolderChecker was successfully uninstalled.")
        success.addButtonWithTitle_("OK")
        system_icon = AppKit.NSImage.imageNamed_("NSApplicationIcon")
        success.setIcon_(system_icon)   
        success.runModal()

        AppKit.NSApp.terminate_(None)
        