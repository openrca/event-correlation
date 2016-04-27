""" Automatically generated documentation for Visualizer """
import logging

from PyQt5.QtCore import Qt
from PySide.QtCore import Signal, QPoint
from PySide.QtGui import QMainWindow, QWidget, QLabel, QVBoxLayout, QPainter, QPainterPath

from core.sequence import Sequence


class EventWidget(QLabel):
    def __init__(self, event, parent=None):
        super().__init__(parent)
        self.eventType = event

        self.setText(str(event.getEventType()))
        self.setAlignment(Qt.AlignCenter)

        self.maxSize = 50
        self.minSize = 10

    def paint(self, width):
        width = min(width, self.maxSize)
        width = max(width, self.minSize)

        self.setFixedSize(width, width)
        self.setStyleSheet("border: 1px solid black; border-radius: {}px".format(str(width // 2)))

    def mousePressEvent(self, event):
        logging.debug("EventWidget clicked")

    def __eq__(self, other):
        if (not isinstance(EventWidget)):
            return False
        return other.eventType == self.eventType

    def __hash__(self):
        return hash(self.eventType)


class SequenceWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sequence = None
        self.eventWidgets = {}

        self.offset = 1
        self.eventY = 70
        self.arcOffset = 50
        self.triangleSize = 5

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        for event, widget in self.eventWidgets.items():
            response = event.getTriggered()

            if (response is None or response.getTimestamp() == -1):
                continue

            triggeredWidget = self.eventWidgets[event.getTriggered()]
            self.__paintArrow(widget, triggeredWidget, painter)
        painter.end()

    def __paintArrow(self, start, end, painter):
        startPos = start.pos()
        startPos.setX(startPos.x() + start.width() / 2)
        endPos = end.pos()
        endPos.setX(endPos.x() + start.width() / 2)
        vertex = QPoint(startPos.x() + (endPos.x() - startPos.x()) / 2, startPos.y() - self.arcOffset)

        triangle1 = QPoint(endPos.x() - self.triangleSize, endPos.y() - self.triangleSize)
        triangle2 = QPoint(endPos.x() + self.triangleSize, endPos.y() - self.triangleSize)

        path = QPainterPath()
        path.moveTo(startPos)
        path.cubicTo(vertex, vertex, endPos)
        path.lineTo(triangle1)
        path.lineTo(triangle2)
        path.lineTo(endPos)

        painter.drawPath(path)

    def paint(self, sequence):
        self.sequence = sequence
        width = self.geometry().width()
        eventWidth = width // self.sequence.getLength() - self.offset

        for i in range(0, self.sequence.getLength()):
            event = self.sequence.getEvent(i)
            widget = EventWidget(event, self)

            widget.move(i * (eventWidth + self.offset), self.eventY)
            widget.paint(eventWidth)
            widget.show()

            self.eventWidgets[event] = widget


class Visualizer(QMainWindow):
    paintSeq = Signal(Sequence)

    def __init__(self):
        super().__init__()
        self.sequenceWidget = None
        self.layout = None
        self.initGui()

    def initGui(self):
        self.setGeometry(100, 300, 1200, 250)

        widget = QWidget()

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

        self.sequenceWidget = SequenceWidget()
        self.layout.addWidget(self.sequenceWidget, 0, 0)

        self.setCentralWidget(widget)
        self.paintSeq.connect(self.sequenceWidget.paint)
