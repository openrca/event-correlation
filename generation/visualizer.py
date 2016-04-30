""" Automatically generated documentation for Visualizer """
import logging

from PySide.QtCore import Signal, QPoint, QRectF
from PySide.QtGui import QMainWindow, QWidget, QVBoxLayout, QPainter, QPainterPath, QGraphicsScene, QGraphicsView, \
    QGraphicsItem, QFont, QFontMetrics, QBrush, QColor

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
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        self.arcOffset = 50
        self.triangleSize = 5

        self.rect = QRectF(start.boundingRect().x(), start.boundingRect().y() - self.arcOffset,
                           end.boundingRect().x() - start.boundingRect().x() + end.boundingRect().width(),
                           self.arcOffset)

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter, option, widget):
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
        painter.fillPath(path, QBrush(QColor(0, 0, 0)))
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
        for i in range(0, self.sequence.getLength()):
            event = self.sequence.getEvent(i)
            widget = EventWidget(event, QPoint(i * (self.eventWidth + self.offset), self.eventY), self.eventWidth)
            self.addItem(widget)
            self.eventWidgets[event] = widget

        for event, widget in self.eventWidgets.items():
            response = event.getTriggered()
            if (response is None or response.getTimestamp() >= self.sequence.getLength()):
                continue

            triggeredWidget = self.eventWidgets[event.getTriggered()]
            self.addItem(ArrowWidget(widget, triggeredWidget))

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

    def setSequence(self, sequence):
        self.view.items().clear()
        self.paintSeq.emit(sequence)
        self.statusBar().showMessage("Loaded sequence")
