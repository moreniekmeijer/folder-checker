import threading
import objc
from AppKit import (
    NSWindow, NSButton, NSTextField, NSPopUpButton, NSScrollView, NSTableView, NSTableColumn,
    NSRunningApplication, NSApplicationActivateIgnoringOtherApps, NSOpenPanel, NSNotificationCenter, 
    NSTextDidChangeNotification, NSImage, NSImageView, NSBundle
)
from Foundation import NSObject
import checker
import config
from logger_setup import logger

logger.info("Starting Cocoa settings GUI")

INTERVAL_OPTIONS = {
    "Every 5 minutes": 300,
    "Every hour": 3600,
    "Every day": 86400,
    "Every week": 604800,
    "Every month": 2592000,
}


class WatchPathsTable(NSObject):
    def initWithPaths_saveCallback_(self, paths, save_callback):
        self = objc.super(WatchPathsTable, self).init()
        self.paths = paths
        self.save_callback = save_callback
        return self

    def numberOfRowsInTableView_(self, tableView):
        return len(self.paths)

    def tableView_objectValueForTableColumn_row_(self, tableView, column, row):
        return self.paths[row]

    def tableView_shouldSelectRow_(self, tableView, row):
        return True

    def addPaths_(self, new_paths):
        self.paths.extend(new_paths)
        self.save_callback()

    def removeSelectedRows_(self, tableView):
        selected = tableView.selectedRowIndexes()
        for i in reversed(range(len(self.paths))):
            if selected.containsIndex_(i):
                self.paths.pop(i)
        tableView.reloadData()
        self.save_callback()


class SettingsWindow:
    def __init__(self):
        self.cfg = config.load_config()

        # --- Window ---
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((200.0, 200.0), (320.0, 460.0)),
            15,  # Closable | Titled | Miniaturizable
            2,   # Buffered
            False
        )
        self.window.setTitle_("Folder Checker Settings")
        self.window.makeKeyAndOrderFront_(None)
        NSRunningApplication.currentApplication().activateWithOptions_(
            NSApplicationActivateIgnoringOtherApps
        )

        content = self.window.contentView()
        y = 440  # start top

        # --- Icon ---
        bundle = NSBundle.mainBundle()
        icon_path = bundle.pathForResource_ofType_("sweeper", "icns")
        if icon_path:
            img = NSImage.alloc().initWithContentsOfFile_(icon_path)
            img.setSize_((64, 64))
            img.setTemplate_(True)
            image_view = NSImageView.alloc().initWithFrame_(((128, y -50), (64, 64)))
            image_view.setImage_(img)
            content.addSubview_(image_view)
        
        y -= 60
        # --- Watch Paths Table ---
        self.watch_paths_data = self.cfg.get("WATCH_PATHS", [])
        self.paths_data_source = WatchPathsTable.alloc().initWithPaths_saveCallback_(
            self.watch_paths_data, self.save_live_settings
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
        # --- Add Path Button ---
        self.add_path_button = NSButton.alloc().initWithFrame_(((70, y), (90, 30)))
        self.add_path_button.setTitle_("Add")
        self.add_path_button.setTarget_(self)
        self.add_path_button.setAction_("addPath:")
        content.addSubview_(self.add_path_button)

        # --- Remove Path Button ---
        self.remove_path_button = NSButton.alloc().initWithFrame_(((160, y), (90, 30)))
        self.remove_path_button.setTitle_("Remove")
        self.remove_path_button.setTarget_(self)
        self.remove_path_button.setAction_("removePath:")
        content.addSubview_(self.remove_path_button)

        # Disable remove button if only one path
        if len(self.watch_paths_data) <= 1:
            self.remove_path_button.setEnabled_(False)


        y -= 60
        # --- Max Size ---
        self.size_label = NSTextField.alloc().initWithFrame_(((20, y), (130, 24)))
        self.size_label.setStringValue_("Max Size (MB):")
        self.size_label.setEditable_(False)
        content.addSubview_(self.size_label)

        self.size_field = NSTextField.alloc().initWithFrame_(((160, y), (80, 24)))
        self.size_field.setStringValue_(str(self.cfg.get("MAX_SIZE_MB", 500)))
        self.size_field.setTarget_(self)
        self.size_field.setToolTip_("Maximum allowed size of files (in MB) in folder to be checked")
        content.addSubview_(self.size_field)

        y -= 40
        # --- Max Files ---
        self.files_label = NSTextField.alloc().initWithFrame_(((20, y), (130, 24)))
        self.files_label.setStringValue_("Max Items:")
        self.files_label.setEditable_(False)
        content.addSubview_(self.files_label)

        self.files_field = NSTextField.alloc().initWithFrame_(((160, y), (80, 24)))
        self.files_field.setStringValue_(str(self.cfg.get("MAX_AMOUNT_ITEMS", 10)))
        self.files_field.setTarget_(self)
        self.files_field.setToolTip_("Maximum amount of items (subfolders and files) in folder to be checked")
        content.addSubview_(self.files_field)

        y -= 40
        """Uncomment to add MAX_INTERACTIVE_FILES option, also adjust all other references."""
        # --- Max Interactive Files ---
        # self.interactive_label = NSTextField.alloc().initWithFrame_(((20, y), (130, 24)))
        # self.interactive_label.setStringValue_("Interactive Files:")
        # self.interactive_label.setEditable_(False)
        # content.addSubview_(self.interactive_label)

        # self.interactive_field = NSTextField.alloc().initWithFrame_(((160, y), (80, 24)))
        # self.interactive_field.setStringValue_(str(self.cfg.get("MAX_INTERACTIVE_FILES", 10)))
        # self.interactive_field.setTarget_(self)
        # self.interactive_field.setToolTip_("Amount of files to be asked to remove when starting clean-up")
        # content.addSubview_(self.interactive_field)

        # y -= 40
        # --- Checker Interval ---
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
        self.interval_dropdown.setTarget_(self)
        self.interval_dropdown.setAction_("intervalChanged:")
        content.addSubview_(self.interval_dropdown)

        y -= 60
        # --- Check Now Button ---
        self.check_button = NSButton.alloc().initWithFrame_(((115, y), (90, 30)))
        self.check_button.setTitle_("Check Now")
        self.check_button.setTarget_(self)
        self.check_button.setAction_("runCheckerNow:")
        content.addSubview_(self.check_button)

        for field in [self.size_field, self.files_field]:
            NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
                self,
                objc.selector(self.fieldChanged_, signature=b'v@:@'),
                NSTextDidChangeNotification,
                None
            )

        y -= 30
        # --- Status label (used for both saved & checked) ---
        self.status_label = NSTextField.alloc().initWithFrame_(((130, y), (100, 24)))
        self.status_label.setEditable_(False)
        self.status_label.setBezeled_(False)
        self.status_label.setDrawsBackground_(False)
        self.status_label.setHidden_(True)
        content.addSubview_(self.status_label)


    # --- Unified label display ---
    def show_temporary_label(self, text: str, duration=1.5):
        self.status_label.setStringValue_(text)
        self.status_label.setHidden_(False)

        def hide():
            import time
            time.sleep(duration)
            self.status_label.setHidden_(True)

        threading.Thread(target=hide, daemon=True).start()


    # --- Live save method ---
    def save_live_settings(self):
        def safe_int(field, default):
            try:
                return int(field.stringValue())
            except ValueError:
                return default

        new_cfg = {
            "WATCH_PATHS": self.paths_data_source.paths,
            "MAX_SIZE_MB": safe_int(self.size_field, self.cfg.get("MAX_SIZE_MB", 500)),
            "MAX_AMOUNT_ITEMS": safe_int(self.files_field, self.cfg.get("MAX_AMOUNT_ITEMS", 10)),
            "MAX_INTERACTIVE_FILES": 100,  # fixed value since field is disabled
            "CHECK_INTERVAL_SEC": INTERVAL_OPTIONS.get(
                self.interval_dropdown.titleOfSelectedItem(), 86400
            )
        }
        config.save_config(new_cfg)
        self.show_temporary_label("✓ Saved")

    # --- Field change actions ---
    def fieldChanged_(self, notification):
        self.save_live_settings()

    def intervalChanged_(self, sender):
        self.save_live_settings()


    # --- Add / Remove Paths ---
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
        if len(self.paths_data_source.paths) <= 1:
            self.remove_path_button.setEnabled_(False)


    # --- Run Checker Now ---
    def runCheckerNow_(self, sender):
        logger.info("Manual 'Check now' clicked")
        try:
            checker.run_checker(interactive=True)
            self.show_temporary_label("✓ Check")
        except Exception as e:
            logger.error(f"Error during manual check: {e}")


def open_settings_window():
    SettingsWindow()
