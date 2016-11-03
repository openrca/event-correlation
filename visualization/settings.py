from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtGui import QAbstractItemView, QPushButton
from PySide.QtGui import QTableWidgetItem, QHeaderView
from PySide.QtGui import QVBoxLayout, QLabel, QTableWidget
from PySide.QtGui import QWidget


class Settings(QWidget):
    close = Signal()

    def __init__(self, parent):
        super().__init__()
        self.highLights = []
        self.hidden = []
        self.__events = []

        self.table = QTableWidget()
        self.save = QPushButton('Save')
        # noinspection PyUnresolvedReferences
        self.save.clicked.connect(self.__saveAndClose)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Settings'))
        layout.addWidget(self.table)
        layout.addWidget(self.save)
        self.setLayout(layout)

        self.close.connect(parent.repaintSequence)

    def setSequence(self, sequence):
        self.__events = sorted(set([e.eventType for e in sequence.events]))

        self.table.setColumnCount(3)
        self.table.setRowCount(len(self.__events))

        for index, key in enumerate(self.__events):
            eventItem = QTableWidgetItem(str(key))
            highLightItem = QTableWidgetItem()
            highLightItem.setCheckState(Qt.Unchecked)
            hideItem = QTableWidgetItem()
            hideItem.setCheckState(Qt.Unchecked)
            self.table.setItem(index, 0, eventItem)
            self.table.setItem(index, 1, highLightItem)
            self.table.setItem(index, 2, hideItem)

        # noinspection PyUnresolvedReferences
        self.table.cellClicked.connect(self.__handleItemClicked)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.resizeColumnsToContents()
        self.table.setHorizontalHeaderLabels(["Event", "HighLight", "Hide"])
        self.table.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    def __handleItemClicked(self, row, column):
        if (column == 0):
            return
        event = self.__events[row]
        item = self.table.item(row, column)

        if (item.checkState() == Qt.Checked):
            if (column == 1):
                self.highLights.append(event)
            if (column == 2):
                self.hidden.append(event)
        else:
            if (column == 1):
                self.highLights.remove(event)
            if (column == 2):
                self.hidden.remove(event)

    def __saveAndClose(self):
        self.close.emit()
        self.hide()
