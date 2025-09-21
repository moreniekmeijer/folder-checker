import os
import shutil
import AppKit


def uninstall_app():
    alert = AppKit.NSAlert.alloc().init()
    alert.setMessageText_("Uninstall FolderChecker?")
    alert.setInformativeText_("This will remove all app data from Application Support and quit the app.")
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
        app_support = os.path.expanduser("~/Library/Application Support/folder-checker")
        if os.path.exists(app_support):
            try:
                shutil.rmtree(app_support)
                print(f"Removed {app_support}")
            except Exception as e:
                print(f"Error removing support folder: {e}")

        app_path = "/Applications/FolderChecker.app"
        if os.path.exists(app_path):
            shutil.rmtree(app_path)

        AppKit.NSApp.terminate_(None)
