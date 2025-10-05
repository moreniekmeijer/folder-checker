import os
import subprocess
import threading
import time
from Foundation import NSObject
from AppKit import (
    NSApplication,
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSImage,
    NSBundle,
    NSWorkspace,
)
import checker
import config
from logger_setup import logger
import settings_window as settings
from notifications import setup_notifications
import uninstall


def add_to_login_items(app_path):
    if not os.path.exists(app_path):
        logger.warning(f"App path does not exist: {app_path}")
        return

    app_name = os.path.basename(app_path)
    script = f'''
    tell application "System Events"
        if not (exists login item "{app_name}") then
            make login item at end with properties {{path:"{app_path}", hidden:false}}
        end if
    end tell
    '''
    try:
        subprocess.run(['osascript', '-e', script], check=True)
        logger.info(f"Added to Login Items: {app_path}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Could not add to Login Items: {e}")


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        logger.info("Application launched")

        def after_permission(granted):
            if not granted:
                logger.warning("User did not grant notification permissions")
                script = 'display dialog "FolderChecker cannot show notifications. Please enable notifications in System Settings > Notifications." buttons {"OK"} default button "OK"'
                subprocess.run(["osascript", "-e", script])
            else:
                logger.info("Notifications are allowed")

        setup_notifications(after_permission)

        cfg = config.load_config()
        if "LAST_RUN_TS" not in cfg:
            cfg["LAST_RUN_TS"] = 0
            config.save_config(cfg)

        self._catch_up_check()

        nc = NSWorkspace.sharedWorkspace().notificationCenter()
        nc.addObserver_selector_name_object_(
            self,
            self.handleWake_,
            "NSWorkspaceDidWakeNotification",
            None
        )

        if not cfg.get("FIRST_RUN_DONE", False):
            try:
                APP_PATH = NSBundle.mainBundle().bundlePath()
                add_to_login_items(APP_PATH)
            except Exception as e:
                logger.warning(f"Could not add to Login Items: {e}")

        self._build_status_item()
        self._build_menu()

        self.checker_enabled = True
        self.checker_timer = None
        self.start_checker_loop()

        if not cfg.get("FIRST_RUN_DONE", False):
            logger.info("First run detected, opening settings window")
            settings.open_settings_window()
            cfg["FIRST_RUN_DONE"] = True
            config.save_config(cfg)
    
    def applicationWillTerminate_(self, notification):
        nc = NSWorkspace.sharedWorkspace().notificationCenter()
        nc.removeObserver_(self)
        logger.info("Application terminating — removed wake observer")


    # -----------------------
    # UI helpers
    # -----------------------
    def _build_status_item(self):
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(-1)

        bundle = NSBundle.mainBundle()

        self.sweeper_enabled = NSImage.alloc().initWithContentsOfFile_(
            bundle.pathForResource_ofType_("sweeper_enabled", "icns")
        )
        self.sweeper_disabled = NSImage.alloc().initWithContentsOfFile_(
            bundle.pathForResource_ofType_("sweeper_disabled", "icns")
        )
        self.icon_enabled = NSImage.alloc().initWithContentsOfFile_(
            bundle.pathForResource_ofType_("enabled", "icns")
        )
        self.icon_disabled = NSImage.alloc().initWithContentsOfFile_(
            bundle.pathForResource_ofType_("disabled", "icns")
        )

        for img in (self.sweeper_enabled, self.sweeper_disabled, self.icon_enabled, self.icon_disabled):
            if img:
                img.setSize_((18, 18))
                img.setTemplate_(True)

        self.statusitem.button().setImage_(self.sweeper_enabled)
        self.statusitem.button().setTitle_("")

    def _build_menu(self):
        menu = NSMenu()

        # toggle checker
        self.toggle_checker_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Disable checker", "toggleChecker:", ""
        )
        self.toggle_checker_item.setImage_(self.icon_enabled)
        menu.addItem_(self.toggle_checker_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # check now
        item1 = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Check now", "checkNow:", ""
        )
        menu.addItem_(item1)

        menu.addItem_(NSMenuItem.separatorItem())

        # open settings
        item2 = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Open settings", "openSettings:", ""
        )
        menu.addItem_(item2)

        # uninstall
        uninstall_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Uninstall…", "uninstallApp:", ""
        )
        uninstall_item.setTarget_(self)
        menu.addItem_(uninstall_item)

        self.statusitem.setMenu_(menu)


    # -----------------------
    # Catch-up logica
    # -----------------------
    def _catch_up_check(self):
        cfg = config.load_config()

        if not cfg.get("FIRST_RUN_DONE", False):
            logger.info("Skipping catch-up check — first run not completed yet")
            return

        interval = cfg.get("CHECK_INTERVAL_SEC", 3600)
        last_run = cfg.get("LAST_RUN_TS", 0)
        now = time.time()

        if now - last_run >= interval:
            logger.info("Catch-up check triggered after sleep/launch")
            try:
                checker.run_checker()
                cfg["LAST_RUN_TS"] = now
                config.save_config(cfg)
            except Exception as e:
                logger.error(f"Error during catch-up check: {e}")


    # -----------------------
    # Wake handler
    # -----------------------
    def handleWake_(self, notification):
        logger.info("Mac woke from sleep — checking if catch-up is needed")
        self._catch_up_check()


    # -----------------------
    # Checker loop
    # -----------------------
    def start_checker_loop(self):
        def run_periodically():
            if not self.checker_enabled:
                logger.info("Checker disabled — skipping run")
                return

            cfg = config.load_config()
            interval = cfg.get("CHECK_INTERVAL_SEC", 3600)

            logger.info(f"Background checker triggered (next run in {interval} sec)")
            try:
                checker.run_checker()
                cfg["LAST_RUN_TS"] = time.time()
                config.save_config(cfg)
            except Exception as e:
                logger.error(f"Error during periodical check: {e}")

            self.checker_timer = threading.Timer(interval, run_periodically)
            self.checker_timer.daemon = True
            self.checker_timer.start()

        run_periodically()

    def stop_checker_loop(self):
        if self.checker_timer:
            self.checker_timer.cancel()
            self.checker_timer = None
            logger.info("Background checker stopped")


    # -----------------------
    # Menu actions
    # -----------------------
    def checkNow_(self, sender):
        logger.info("Manual 'Check now' clicked")
        try:
            checker.run_checker()
        except Exception as e:
            logger.error(f"Error during manual check: {e}")

    def openSettings_(self, sender):
        logger.info("Opening settings window")
        settings.open_settings_window()

    def uninstallApp_(self, sender):
        uninstall.uninstall_app()

    def toggleChecker_(self, sender):
        if self.checker_enabled:
            self.checker_enabled = False
            self.stop_checker_loop()
            self.toggle_checker_item.setTitle_("Enable checker")
            self.statusitem.button().setImage_(self.sweeper_disabled)
            self.toggle_checker_item.setImage_(self.icon_enabled)
            logger.info("Checker disabled by user")
        else:
            self.checker_enabled = True
            self.start_checker_loop()
            self.toggle_checker_item.setTitle_("Disable checker")
            self.statusitem.button().setImage_(self.sweeper_enabled)
            self.toggle_checker_item.setImage_(self.icon_disabled)
            logger.info("Checker enabled by user")


if __name__ == "__main__":
    logger.info("Starting NSApplication loop")
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()