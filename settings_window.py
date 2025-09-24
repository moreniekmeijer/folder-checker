import config
import threading, objc
from AppKit import (
    NSWindow, NSButton, NSTextField, NSPopUpButton, NSScrollView, NSTableView, NSTableColumn,
    NSRunningApplication, NSApplicationActivateIgnoringOtherApps, NSOpenPanel,
    NSNotificationCenter, NSTextDidChangeNotification, NSImage, NSImageView, NSBundle
)
from Foundation import NSObject
from settings_model import SettingsModel, INTERVAL_OPTIONS
from watch_paths import WatchPathsDataSource
import checker
from logger_setup import logger

_settings_window_instance = None


class SettingsWindowDelegate(NSObject):
    def windowWillClose_(self, notification):
        global _settings_window_instance
        _settings_window_instance = None


class SettingsWindowController:
    def __init__(self):
        self.model = SettingsModel()
        self.cfg = self.model.all()

        self.window = self._create_window()
        self._build_ui()
        self._bind_events()

    # --- Window lifecycle ---
    def _create_window(self):
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((200.0, 200.0), (320.0, 460.0)),
            15, 2, False
        )
        window.setTitle_("Folder Checker Settings")
        return window

    def show(self):
        self.window.makeKeyAndOrderFront_(None)
        NSRunningApplication.currentApplication().activateWithOptions_(
            NSApplicationActivateIgnoringOtherApps
        )

    # --- UI building ---
    def _build_ui(self):
        content = self.window.contentView()
        y = 440

        # App icon
        bundle = NSBundle.mainBundle()
        icon_path = bundle.pathForResource_ofType_("sweeper", "icns")
        if icon_path:
            img = NSImage.alloc().initWithContentsOfFile_(icon_path)
            img.setSize_((64, 64))
            img.setTemplate_(True)
            image_view = NSImageView.alloc().initWithFrame_(((128, y - 50), (64, 64)))
            image_view.setImage_(img)
            content.addSubview_(image_view)

        y -= 60
        # Paths table
        self.watch_paths_data = self.cfg.get("WATCH_PATHS", [])
        self.paths_data_source = WatchPathsDataSource.alloc().initWithPaths_saveCallback_(
            self.watch_paths_data, self.save_settings
        )

        self.paths_table = NSTableView.alloc().initWithFrame_(((0, 0), (290, 100)))
        column = NSTableColumn.alloc().initWithIdentifier_("Path")
        column.setWidth_(280)
        column.setTitle_("Paths of folders to be checked")
        self.paths_table.addTableColumn_(column)
        self.paths_table.setDataSource_(self.paths_data_source)
        self.paths_table.setDelegate_(self.paths_data_source)
        self.paths_table.setAllowsMultipleSelection_(True)

        self.scroll_view = NSScrollView.alloc().initWithFrame_(((20, y - 100), (280, 100)))
        self.scroll_view.setDocumentView_(self.paths_table)
        self.scroll_view.setHasVerticalScroller_(True)
        self.scroll_view.setBorderType_(1)
        content.addSubview_(self.scroll_view)

        y -= 140
        self.add_path_button = NSButton.alloc().initWithFrame_(((70, y), (90, 30)))
        self.add_path_button.setTitle_("Add")
        self.add_path_button.setTarget_(self)
        self.add_path_button.setAction_("addPath:")
        content.addSubview_(self.add_path_button)

        self.remove_path_button = NSButton.alloc().initWithFrame_(((160, y), (90, 30)))
        self.remove_path_button.setTitle_("Remove")
        self.remove_path_button.setTarget_(self)
        self.remove_path_button.setAction_("removePath:")
        content.addSubview_(self.remove_path_button)
        self.remove_path_button.setEnabled_(len(self.watch_paths_data) > 1)

        y -= 60
        # Max size
        self.size_field = self._make_labeled_field(content, "Max Size (MB):", (20, y), self.cfg.get("MAX_SIZE_MB", 500))

        y -= 40
        # Max items
        self.files_field = self._make_labeled_field(content, "Max Items:", (20, y), self.cfg.get("MAX_AMOUNT_ITEMS", 10))

        y -= 40
        # Interval
        self.interval_label = NSTextField.alloc().initWithFrame_(((20, y), (130, 24)))
        self.interval_label.setStringValue_("Checker Interval:")
        self.interval_label.setEditable_(False)
        content.addSubview_(self.interval_label)

        self.interval_dropdown = NSPopUpButton.alloc().initWithFrame_(((160, y), (140, 26)))
        for label in INTERVAL_OPTIONS.keys():
            self.interval_dropdown.addItemWithTitle_(label)
        current_interval = self.cfg.get("CHECK_INTERVAL_SEC", 86400)
        for label, seconds in INTERVAL_OPTIONS.items():
            if seconds == current_interval:
                self.interval_dropdown.selectItemWithTitle_(label)
                break
        content.addSubview_(self.interval_dropdown)

        y -= 60
        # Check now button
        self.check_button = NSButton.alloc().initWithFrame_(((115, y), (90, 30)))
        self.check_button.setTitle_("Check Now")
        self.check_button.setTarget_(self)
        self.check_button.setAction_("runCheckerNow:")
        content.addSubview_(self.check_button)

        y -= 30
        # Status label
        self.status_label = NSTextField.alloc().initWithFrame_(((130, y), (100, 24)))
        self.status_label.setEditable_(False)
        self.status_label.setBezeled_(False)
        self.status_label.setDrawsBackground_(False)
        self.status_label.setHidden_(True)
        content.addSubview_(self.status_label)

    def _make_labeled_field(self, content, label_text, pos, value):
        label = NSTextField.alloc().initWithFrame_(((pos[0], pos[1]), (130, 24)))
        label.setStringValue_(label_text)
        label.setEditable_(False)
        content.addSubview_(label)

        field = NSTextField.alloc().initWithFrame_(((160, pos[1]), (80, 24)))
        field.setStringValue_(str(value))
        content.addSubview_(field)
        return field

    # --- Event binding ---
    def _bind_events(self):
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self,
            objc.selector(self.fieldChanged_, signature=b'v@:@'),
            NSTextDidChangeNotification,
            None
        )
        self.interval_dropdown.setTarget_(self)
        self.interval_dropdown.setAction_("intervalChanged:")

    # --- Actions ---
    def save_settings(self):
        def safe_int(field, default):
            try:
                return int(field.stringValue())
            except ValueError:
                return default

        updates = ({
            "WATCH_PATHS": self.paths_data_source.paths,
            "MAX_SIZE_MB": safe_int(self.size_field, self.cfg.get("MAX_SIZE_MB", 500)),
            "MAX_AMOUNT_ITEMS": safe_int(self.files_field, self.cfg.get("MAX_AMOUNT_ITEMS", 10)),
            "CHECK_INTERVAL_SEC": INTERVAL_OPTIONS.get(
                self.interval_dropdown.titleOfSelectedItem(), 86400
            )
        })
        config.save_config(updates)
        self.show_temporary_label("✓ Saved")

    def show_temporary_label(self, text, duration=1.5):
        self.status_label.setStringValue_(text)
        self.status_label.setHidden_(False)

        def hide():
            import time
            time.sleep(duration)
            self.status_label.setHidden_(True)

        threading.Thread(target=hide, daemon=True).start()

    def fieldChanged_(self, notification):
        self.save_settings()

    def intervalChanged_(self, sender):
        self.save_settings()

    def addPath_(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseDirectories_(True)
        panel.setCanChooseFiles_(False)
        panel.setAllowsMultipleSelection_(True)
        if panel.runModal() == 1:
            new_paths = [str(url.path()) for url in panel.URLs()]
            self.paths_data_source.addPaths_(new_paths)
            self.paths_table.reloadData()
            self.remove_path_button.setEnabled_(True)

    def removePath_(self, sender):
        if len(self.paths_data_source.paths) <= 1:
            logger.warning("Cannot remove last watch path")
            return
        self.paths_data_source.removeSelectedRows_(self.paths_table)
        self.remove_path_button.setEnabled_(len(self.paths_data_source.paths) > 1)

    def runCheckerNow_(self, sender):
        logger.info("Manual 'Check now' clicked")
        try:
            checker.run_checker(interactive=True)
            self.show_temporary_label("✓ Check")
        except Exception as e:
            logger.error(f"Error during manual check: {e}")


def open_settings_window():
    global _settings_window_instance
    if _settings_window_instance is None:
        _settings_window_instance = SettingsWindowController()
        _settings_window_instance.delegate = SettingsWindowDelegate.alloc().init()
        _settings_window_instance.window.setDelegate_(_settings_window_instance.delegate)
    _settings_window_instance.show()
