from source_app.utils import *

class PackComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)

        self._source_model = QStandardItemModel(self)
        self.setModel(self._source_model)
        self.rows = {}

    def createRow(self, text, userData=None):
        item = QStandardItem(text)
        if userData is not None:
            item.setData(userData, Qt.ItemDataRole.UserRole)
        return item

    def addItem(self, text, userData=None):
        self._source_model.appendRow(self.createRow(text, userData))

    def addItems(self, texts):
        for t in texts:
            self.addItem(t)

    def setItems(self, texts):
        self._source_model.beginResetModel()
        self._source_model.removeRows(0, self.count())
        self._source_model.endResetModel()
        self.addItems(texts)

    def currentData(self, role=Qt.ItemDataRole.UserRole):
        idx = self._proxy_model.index(self.currentIndex(), 0)
        src_idx = self._proxy_model.mapToSource(idx)
        item = self._source_model.itemFromIndex(src_idx)
        return item.data(role) if item else None