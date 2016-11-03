""" Automatically generated documentation for Visualizer """
import logging
import math
import os
import sys

from PySide.QtCore import Signal, QPoint, QRectF
from PySide.QtGui import QMainWindow, QWidget, QVBoxLayout, QPainter, QPainterPath, QGraphicsScene, QGraphicsView, \
    QGraphicsItem, QFont, QFontMetrics, QBrush, QColor, QPen, QAction, QFileDialog, QMessageBox, QApplication

import core
from core.rule import Rule
from core.sequence import Sequence
from provider import generator
from visualization.details import DetailsContainer
from visualization.settings import Settings


class EventWidget(QGraphicsItem):
    def __init__(self, event, highLight, pos, size, parent=None):
        super().__init__()
        self._eventType = event
        self._callbackParam = None
        self.__highLight = highLight
        self.__pos = pos
        self.__size = min(max(size, 10), 50)
        self.__parent = parent
        self.__rect = QRectF(self.__pos.x(), self.__pos.y(), self.__size, self.__size)

        self.setToolTip(event.eventType)

    def boundingRect(self):
        return self.__rect

    def paint(self, painter: QPainter, option, widget):
        size = self.__getTextSize()
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        if (self.__highLight):
            painter.setBrush(QBrush(QColor(150, 150, 150)))

        painter.drawEllipse(self.boundingRect())
        if (len(self._eventType.getExternalRepresentation()) <= 3):
            painter.drawText(self.__pos.x() + (self.__size - size[0]) // 2,
                             self.__pos.y() + (self.__size + size[1]) // 2,
                             self._eventType.getExternalRepresentation())

    def __getTextSize(self):
        font = QFont()
        metric = QFontMetrics(font)
        width = metric.width(self._eventType.getExternalRepresentation())
        height = metric.width(self._eventType.getExternalRepresentation())
        return (width, height)

    def mouseDoubleClickEvent(self, event):
        if (self.__parent is not None):
            self.__parent.detailsSignal.emit(self._callbackParam)

    def __eq__(self, other):
        if (not isinstance(other, EventWidget)):
            return False
        return other._eventType == self._eventType

    def __hash__(self):
        return hash(self._eventType)


class ArrowWidget(QGraphicsItem):
    def __init__(self, start, end, rule):
        super().__init__()
        self.__start = start
        self.__end = end
        self.__rule = rule
        self.arcOffset = 50
        self.triangleSize = 5

        startX = start.boundingRect().x()
        endX = end.boundingRect().x()

        if (startX > endX):
            tmp = startX
            startX = endX
            endX = tmp

        self.rect = QRectF(startX, start.boundingRect().y() - self.arcOffset,
                           endX - startX + end.boundingRect().width(),
                           self.arcOffset)

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter, option, widget):
        color = 0
        if (self.__rule is not None):
            # noinspection PyProtectedMember
            distance = self.__end._eventType.timestamp - self.__start._eventType.timestamp
            prob = self.__rule.distributionResponse.getRelativePdf(distance)
            color = min(200, (1 - prob) * 255)
        color = QColor(color, color, color)

        painter.setPen(QPen(color))

        startRect = self.__start.boundingRect()
        endRect = self.__end.boundingRect()

        startPos = QPoint(startRect.x() + startRect.width() // 2, startRect.y())
        endPos = QPoint(endRect.x() + startRect.width() // 2, endRect.y())
        vertex = QPoint(startPos.x() + (endPos.x() - startPos.x()) / 2, startPos.y() - self.arcOffset)

        # draw arc
        path = QPainterPath()
        path.moveTo(startPos)
        path.cubicTo(vertex, vertex, endPos)
        painter.drawPath(path)
        angle = path.angleAtPercent(1)

        # draw arrow head
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(-self.triangleSize, -self.triangleSize)
        path.lineTo(self.triangleSize, -self.triangleSize)
        path.lineTo(0, 0)

        painter.save()
        painter.translate(endPos)
        painter.rotate(270 - angle)
        painter.fillPath(path, QBrush(color))
        painter.restore()


class SequenceWidget(QGraphicsScene):
    detailsSignal = Signal(Rule)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__sequence = None
        self.__eventWidgets = {}
        self.__detailsView = None

        self.offset = 10
        self.eventWidth = 20
        self.eventY = 0

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
                widget = EventWidget(event2, event2.eventType in highLight,
                                     QPoint(eventCount * (self.eventWidth + self.offset), self.eventY),
                                     self.eventWidth, self)
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

            if (event.triggered in self.__eventWidgets):
                triggeredWidget = self.__eventWidgets[event.triggered]
                self.addItem(ArrowWidget(widget, triggeredWidget, rule))

                # set up callbacks
                widget._callbackParam = rule
                triggeredWidget._callbackParam = rule

    def __showDetails(self, rule):
        if (rule is None):
            self.parent().statusBar().showMessage("No details available")
            return
        # Store instance to prevent premature deletion
        self.__detailsView = DetailsContainer(self.__sequence, rule)
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
