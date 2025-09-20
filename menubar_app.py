from Foundation import NSObject
from AppKit import NSApplication, NSStatusBar, NSMenu, NSMenuItem, NSImage, NSBundle
import checker
import config
import threading
from logger_setup import logger
import settings_gui as settings


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        logger.info("Application launched")

        # --- Build menubar ---
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(-1)

        bundle = NSBundle.mainBundle()
        self.icon_enabled_path = bundle.pathForResource_ofType_("icon", "icns")
        self.icon_disabled_path = bundle.pathForResource_ofType_("icon_disabled", "icns")
        self.icon_enabled = NSImage.alloc().initWithContentsOfFile_(self.icon_enabled_path)
        self.icon_disabled = NSImage.alloc().initWithContentsOfFile_(self.icon_disabled_path)

        for img in (self.icon_enabled, self.icon_disabled):
            if img:
                img.setSize_((18, 18))

        # Default: enabled icon
        self.statusitem.button().setImage_(self.icon_enabled)
        self.statusitem.button().setTitle_("")

        # --- Build menu ---
        menu = NSMenu()

        item1 = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Check now", "checkNow:", ""
        )
        menu.addItem_(item1)

        item2 = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Open settings", "openSettings:", ""
        )
        menu.addItem_(item2)

        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_( 
            "Quit", "terminate:", "" 
        ) 
        menu.addItem_(quit_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # Toggle item (Enable/Disable checker)
        self.toggle_checker_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Disable checker", "toggleChecker:", ""
        )
        menu.addItem_(self.toggle_checker_item)

        self.statusitem.setMenu_(menu)

        # --- Checker loop state ---
        self.checker_enabled = True
        self.checker_timer = None
        self.start_checker_loop()

    # --- Checker background loop ---
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
            except Exception as e:
                logger.error(f"Error during periodical check: {e}")

            # Restart timer
            self.checker_timer = threading.Timer(interval, run_periodically)
            self.checker_timer.daemon = True
            self.checker_timer.start()

        run_periodically()

    def stop_checker_loop(self):
        if self.checker_timer:
            self.checker_timer.cancel()
            self.checker_timer = None
            logger.info("Background checker stopped")

    # --- Menu actions ---
    def checkNow_(self, sender):
        """Uncomment to disable 'Check now' when checker is disabled."""
        # if not self.checker_enabled:
        #     logger.info("Check now clicked, but checker is disabled")
        #     return

        logger.info("Manual 'Check now' clicked")
        try:
            checker.run_checker()
        except Exception as e:
            logger.error(f"Error during manual check: {e}")

    def openSettings_(self, sender):
        logger.info("Opening settings window")
        settings.open_settings_window()

    def toggleChecker_(self, sender):
        if self.checker_enabled:
            self.checker_enabled = False
            self.stop_checker_loop()
            self.toggle_checker_item.setTitle_("Enable checker")
            self.statusitem.button().setImage_(self.icon_disabled)
            logger.info("Checker disabled by user")
        else:
            self.checker_enabled = True
            self.start_checker_loop()
            self.toggle_checker_item.setTitle_("Disable checker")
            self.statusitem.button().setImage_(self.icon_enabled)
            logger.info("Checker enabled by user")


if __name__ == "__main__":
    logger.info("Starting NSApplication loop")
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()
