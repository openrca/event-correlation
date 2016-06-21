""" Automatically generated documentation for Visualizer """
import logging
import math
import os
import sys
import threading

from PySide.QtCore import Signal, QPoint, QRectF
from PySide.QtGui import QMainWindow, QWidget, QVBoxLayout, QPainter, QPainterPath, QGraphicsScene, QGraphicsView, \
    QGraphicsItem, QFont, QFontMetrics, QBrush, QColor, QPen, QAction, QFileDialog, QMessageBox, QApplication

import core
import generation
import visualization
from core.sequence import Sequence


class EventWidget(QGraphicsItem):
    def __init__(self, event, pos, size):
        super().__init__()
        self.eventType = event
        self.maxSize = 50
        self.minSize = 10
        self.size = min(max(size, self.minSize), self.maxSize)
        self.pos = pos

    def boundingRect(self):
        return QRectF(self.pos.x(), self.pos.y(), self.size, self.size)

    def paint(self, painter: QPainter, option, widget):
        size = self.getTextSize()
        painter.drawText(self.pos.x() + (self.size - size[0]) // 2, self.pos.y() + (self.size + size[1]) // 2,
                         self.eventType.getExternalRepresentation())
        painter.drawEllipse(self.boundingRect())

    def getTextSize(self):
        font = QFont()
        metric = QFontMetrics(font)
        width = metric.width(self.eventType.getExternalRepresentation())
        height = metric.width(self.eventType.getExternalRepresentation())
        return (width, height)

    def mousePressEvent(self, event):
        logging.debug("EventWidget clicked")

    def __eq__(self, other):
        if (not isinstance(other, EventWidget)):
            return False
        return other.eventType == self.eventType

    def __hash__(self):
        return hash(self.eventType)


class ArrowWidget(QGraphicsItem):
    def __init__(self, start, end, rule):
        super().__init__()
        self.start = start
        self.end = end
        self.rule = rule
        self.arcOffset = 50
        self.triangleSize = 5

        self.rect = QRectF(start.boundingRect().x(), start.boundingRect().y() - self.arcOffset,
                           end.boundingRect().x() - start.boundingRect().x() + end.boundingRect().width(),
                           self.arcOffset)

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter, option, widget):
        color = 0
        if (self.rule is not None):
            distance = self.end.eventType.timestamp - self.start.eventType.timestamp
            prob = self.rule.distribution.getPDFValue(distance) / self.rule.distribution.getMaximumPDF()
            color = (1 - prob) * 256
        color = QColor(color, color, color)

        painter.setPen(QPen(color))

        startRect = self.start.boundingRect()
        endRect = self.end.boundingRect()

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sequence = None
        self.eventWidgets = {}

        self.offset = 10
        self.eventWidth = 20
        self.eventY = 0

    def paint(self, sequence):
        self.sequence = sequence

        # truncate sequence for faster rendering
        if (len(sequence) > 500):
            logging.info("Truncating sequence to 500 events to limit rendering time")
            seq = Sequence(sequence.events[0: 500], math.ceil(sequence.events[499].timestamp) + 1, sequence.rules,
                           sequence.calculatedRules)
            self.sequence = seq

        eventCount = 0
        for i in range(self.sequence.length):
            for event in self.sequence.getEvent(i):
                widget = EventWidget(event, QPoint(eventCount * (self.eventWidth + self.offset), self.eventY),
                                     self.eventWidth)
                self.addItem(widget)
                self.eventWidgets[event] = widget
                eventCount += 1

        for event, widget in self.eventWidgets.items():
            response = event.triggered
            if (response is None or response.timestamp >= self.sequence.length):
                continue

            rule = sequence.getCalculatedRule(event, response)
            if (rule is None):
                rule = sequence.getRule(event, response)

            if (event.triggered in self.eventWidgets):
                triggeredWidget = self.eventWidgets[event.triggered]
                self.addItem(ArrowWidget(widget, triggeredWidget, rule))

    def cleanUp(self):
        self.sequence = None
        self.eventWidgets = {}
        self.clear()


class Visualizer(QMainWindow):
    paintSeq = Signal(Sequence)

    def __init__(self):
        super().__init__()
        self.sequenceWidget = None
        self.layout = None
        self.view = None
        self.initGui()
        self.initActions()

    def initGui(self):
        self.setGeometry(100, 300, 1200, 250)
        self.setWindowTitle("Sequence Visualizer")

        widget = QWidget()

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

        self.view = QGraphicsView()
        self.layout.addWidget(self.view, 0, 0)

        self.sequenceWidget = SequenceWidget(self)
        self.view.setScene(self.sequenceWidget)

        self.setCentralWidget(widget)
        self.paintSeq.connect(self.sequenceWidget.paint)

        self.statusBar().showMessage("Sequence Visualizer")

    # noinspection PyUnresolvedReferences
    def initActions(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')
        sequenceMenu = menuBar.addMenu('Sequence')

        generateAction = QAction('Generate Sequence', self)
        generateAction.setShortcut('Ctrl+G')
        generateAction.setStatusTip('Generate new sequence')
        generateAction.triggered.connect(self.createSequence)
        sequenceMenu.addAction(generateAction)

        loadAction = QAction('Load Sequence', self)
        loadAction.setShortcut('Ctrl+O')
        loadAction.setStatusTip('Load sequence')
        loadAction.triggered.connect(self.loadSequence)
        sequenceMenu.addAction(loadAction)

        saveAction = QAction('Save Sequence', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save current sequence')
        saveAction.triggered.connect(self.saveSequence)
        sequenceMenu.addAction(saveAction)

        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def loadSequence(self):
        fileName = QFileDialog.getOpenFileName(self, "Load Sequence", os.path.expanduser("~"))[0]
        if (len(fileName) == 0):
            return

        print("Loading sequence from file " + fileName)
        try:
            seq = core.sequence.loadFromFile(fileName)

            threading.Thread(target=visualization.showAllDistributions, args=(seq,)).start()

            self.statusBar().showMessage("Loaded sequence " + fileName)
        except ValueError as ex:
            msg = "Unable to load sequence: " + str(ex)
            print(msg)
            messageBox = QMessageBox()
            messageBox.setText(msg)
            messageBox.exec()
            return
        self.setSequence(seq)

    def saveSequence(self):
        fileName = QFileDialog.getSaveFileName(self, "Load Sequence", os.path.expanduser("~"))[0]
        if (len(fileName) == 0):
            return
        if (fileName[-4:] != ".seq"):
            fileName += ".seq"

        print("Saving sequence to file " + fileName)
        try:
            self.sequenceWidget.sequence.store(fileName)
            self.statusBar().showMessage("Stored sequence in " + fileName)
        except (OSError, IOError) as ex:
            msg = "Unable to store sequence: " + str(ex)
            print(msg)
            messageBox = QMessageBox()
            messageBox.setText(msg)
            messageBox.exec()
            return

    def createSequence(self):
        sequence = generation.createSequences()
        self.setSequence(sequence)

    def setSequence(self, sequence):
        self.view.items().clear()
        self.sequenceWidget.cleanUp()
        self.paintSeq.emit(sequence)
        self.sequenceWidget.update()
        self.statusBar().showMessage("Loaded sequence")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    sys.exit(app.exec_())
