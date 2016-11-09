""" Automatically generated documentation for Visualizer """
import logging
import math
import os
import sys

from PySide.QtCore import Signal, QPoint
from PySide.QtGui import QMainWindow, QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QAction, QFileDialog, \
    QMessageBox, QApplication

import core
from core.rule import Rule
from core.sequence import Sequence
from visualization import EventWidget, ArrowWidget
from visualization.dependencies import DependenciesView
from visualization.details import DetailsContainer
from visualization.settings import Settings


class ResponsiveEventWidget(EventWidget):
    def __init__(self, event, highLight, pos, size, parent=None):
        super().__init__(event, pos, highLight, size)
        self._callbackParam = None
        self.__parent = parent

    def mouseDoubleClickEvent(self, event):
        if (self.__parent is not None):
            self.__parent.detailsSignal.emit(self._callbackParam)


class SequenceWidget(QGraphicsScene):
    detailsSignal = Signal(Rule)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__sequence = None
        self.__eventWidgets = {}
        self.__detailsView = DetailsContainer()

        self.__offset = 10
        self.__eventWidth = 20
        self.__eventY = 0

        self.detailsSignal.connect(self.__showDetails)

    def paint(self, sequence, highLight, hidden):
        self.__sequence = sequence

        # truncate sequence for faster rendering
        renderLimit = 1000
        if (len(sequence) > renderLimit):
            logging.info("Truncating sequence to {} events to limit rendering time".format(renderLimit))
            self.__sequence = Sequence(sequence.events[0: renderLimit],
                                       math.ceil(sequence.events[renderLimit - 1].timestamp) + 1,
                                       sequence.rules, sequence.calculatedRules)

        eventCount = 0
        prevTime = -1
        for event in self.__sequence.events:
            padding = sequence.getPaddedEvent(event, prevTime)
            prevTime = event.timestamp
            for event2 in padding:
                point = QPoint(eventCount * (self.__eventWidth + self.__offset), self.__eventY)
                widget = ResponsiveEventWidget(event2, event2.eventType in highLight, point, self.__eventWidth, self)
                self.addItem(widget)
                self.__eventWidgets[event2] = widget
                eventCount += 1

        for event, widget in self.__eventWidgets.items():
            response = event.triggered
            if (response is None or response.timestamp >= self.__sequence.length
                or event.eventType in hidden or response.eventType in hidden):
                continue

            rule = sequence.getCalculatedRule(event, response)
            if (rule is None):
                rule = sequence.getRule(event, response)
            if (rule is None):
                continue

            if (event.triggered in self.__eventWidgets):
                triggeredWidget = self.__eventWidgets[event.triggered]
                self.addItem(self.__createArrow(event, rule, widget, triggeredWidget))

                # set up callbacks
                widget._callbackParam = rule
                triggeredWidget._callbackParam = rule

    @staticmethod
    def __createArrow(event, rule, widget, triggeredWidget):
        distance = event.triggered.timestamp - event.timestamp
        prob = rule.distributionResponse.getRelativePdf(distance)
        color = min(200, (1 - prob) * 255)

        startRect = widget.boundingRect()
        endRect = triggeredWidget.boundingRect()

        if (startRect.x() > endRect.x()):
            tmp = startRect
            startRect = endRect
            endRect = tmp

        start = QPoint(startRect.x() + startRect.width() // 2, startRect.y())
        end = QPoint(endRect.x() + startRect.width() // 2, endRect.y())

        return ArrowWidget(start, end, color, 50)

    def __showDetails(self, rule):
        if (rule is None):
            self.parent().statusBar().showMessage("No details available")
            return
        self.__detailsView.setData(self.__sequence, rule)
        self.__detailsView.show()

    def cleanUp(self):
        self.__eventWidgets = {}
        self.clear()


class Visualizer(QMainWindow):
    __paintSeq = Signal(Sequence, list, list)

    def __init__(self):
        super().__init__()
        self.__sequenceWidget = None
        self.__view = None
        self.__sequence = None
        self.__dependenciesView = DependenciesView()
        self.__settingsView = Settings(self)
        self.__initGui()
        self.__initActions()

    def __initGui(self):
        self.setGeometry(100, 300, 1200, 250)
        self.setWindowTitle("Sequence Visualizer")

        widget = QWidget()

        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.__view = QGraphicsView()
        layout.addWidget(self.__view, 0, 0)

        self.__sequenceWidget = SequenceWidget(self)
        self.__view.setScene(self.__sequenceWidget)

        self.setCentralWidget(widget)
        self.__paintSeq.connect(self.__sequenceWidget.paint)

        self.statusBar().showMessage("Sequence Visualizer")

    # noinspection PyUnresolvedReferences
    def __initActions(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')
        sequenceMenu = menuBar.addMenu('Sequence')

        loadAction = QAction('Load Sequence', self)
        loadAction.setShortcut('Ctrl+O')
        loadAction.setStatusTip('Load sequence')
        loadAction.triggered.connect(self.__loadSequence)
        sequenceMenu.addAction(loadAction)

        saveAction = QAction('Save Sequence', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save current sequence')
        saveAction.triggered.connect(self.__saveSequence)
        sequenceMenu.addAction(saveAction)

        dependenciesAction = QAction('Dependencies', self)
        dependenciesAction.setShortcut('Ctrl+D')
        dependenciesAction.setStatusTip('Show dependencies')
        dependenciesAction.triggered.connect(self.__dependenciesView.show)
        fileMenu.addAction(dependenciesAction)

        settingsAction = QAction('Settings', self)
        settingsAction.setShortcut('Ctrl+Shift+S')
        settingsAction.setStatusTip('Open settings')
        settingsAction.triggered.connect(self.__openSettings)
        fileMenu.addAction(settingsAction)

        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def __loadSequence(self):
        # noinspection PyCallByClass
        fileName = QFileDialog.getOpenFileName(self, "Load Sequence", os.path.expanduser("~"))[0]
        if (len(fileName) == 0):
            return

        logging.info("Loading sequence from file " + fileName)
        try:
            seq = core.sequence.loadFromFile(fileName)
            self.statusBar().showMessage("Loaded sequence " + fileName)
        except ValueError as ex:
            msg = "Unable to load sequence: " + str(ex)
            logging.warning(msg)
            messageBox = QMessageBox()
            messageBox.setText(msg)
            messageBox.exec()
            return
        self.setSequence(seq)

    def __saveSequence(self):
        # noinspection PyCallByClass
        fileName = QFileDialog.getSaveFileName(self, "Load Sequence", os.path.expanduser("~"))[0]
        if (len(fileName) == 0):
            return
        if (fileName[-4:] != ".seq"):
            fileName += ".seq"

        logging.info("Saving sequence to file " + fileName)
        try:
            self.__sequenceWidget.sequence.store(fileName)
            self.statusBar().showMessage("Stored sequence in " + fileName)
        except (OSError, IOError) as ex:
            msg = "Unable to store sequence: " + str(ex)
            logging.warning(msg)
            messageBox = QMessageBox()
            messageBox.setText(msg)
            messageBox.exec()
            return

    def setSequence(self, sequence):
        self.__sequence = sequence
        self.__settingsView.setSequence(sequence)
        self.repaintSequence()
        self.statusBar().showMessage("Loaded sequence")

    def setDependencyRoot(self, root):
        if (self.__sequence is None):
            return
        self.__dependenciesView.setData(root, self.__sequence)

    def repaintSequence(self):
        self.__view.items().clear()
        self.__sequenceWidget.cleanUp()
        self.__paintSeq.emit(self.__sequence, self.__settingsView.highLights, self.__settingsView.hidden)
        self.__sequenceWidget.update()
        self.statusBar().showMessage("Redraw sequence")

    def __openSettings(self):
        self.__settingsView.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    sys.exit(app.exec_())
