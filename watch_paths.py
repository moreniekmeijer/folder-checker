import objc
from Foundation import NSObject


class WatchPathsDataSource(NSObject):
    def initWithPaths_saveCallback_(self, paths, save_callback):
        self = objc.super(WatchPathsDataSource, self).init()
        self.paths = paths
        self.save_callback = save_callback
        return self

    def numberOfRowsInTableView_(self, tableView):
        return len(self.paths)

    def tableView_objectValueForTableColumn_row_(self, tableView, column, row):
        return self.paths[row]

    def addPaths_(self, new_paths):
        self.paths.extend(new_paths)
        self.save_callback()

    def removeSelectedRows_(self, tableView):
        selected = tableView.selectedRowIndexes()
        self.paths = [p for i, p in enumerate(self.paths) if not selected.containsIndex_(i)]
        tableView.reloadData()
        self.save_callback()
