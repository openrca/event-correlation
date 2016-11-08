import sys

from PySide.QtCore import QPoint, QRectF
from PySide.QtGui import QApplication, QBrush, QColor, QFont, QFontMetrics, QGraphicsItem, QPainter, QPainterPath, QPen


def showVisualizer(sequence=None):
    from visualization.visualizer import Visualizer
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    if (sequence is not None):
        v.setSequence(sequence)

    sys.exit(app.exec_())


class EventWidget(QGraphicsItem):
    def __init__(self, event, pos, highLight=False, size=20):
        super().__init__()
        self._eventType = event
        self.__highLight = highLight
        self.__pos = pos
        self.__size = size
        self.__rect = QRectF(self.__pos.x(), self.__pos.y(), self.__size, self.__size)

        self.setToolTip(event.eventType)

    def boundingRect(self):
        return self.__rect

    def paint(self, painter: QPainter, option, widget):
        size = self.__getTextSize()
        painter.setRenderHint(QPainter.Antialiasing)
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

    def __eq__(self, other):
        if (not isinstance(other, EventWidget)):
            return False
        return other._eventType == self._eventType

    def __hash__(self):
        return hash(self._eventType)


class ArrowWidget(QGraphicsItem):
    def __init__(self, start, end, color=0, arcOffset=0):
        super().__init__()
        self.__start = start
        self.__end = end
        self.__color = QColor(color, color, color)
        self.__arcOffset = arcOffset
        self.__triangleSize = 5

        self.__rect = QRectF(start.x(), start.y() - max(self.__triangleSize, self.__arcOffset),
                             end.x() - start.x() + self.__triangleSize, max(self.__triangleSize, self.__arcOffset))

    def boundingRect(self):
        return self.__rect

    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(self.__color))
        vertex = QPoint(self.__start.x() + (self.__end.x() - self.__start.x()) / 2, self.__start.y() - self.__arcOffset)

        # draw arc
        path = QPainterPath()
        path.moveTo(self.__start)
        if (self.__arcOffset == 0):
            path.lineTo(self.__end)
        else:
            path.cubicTo(vertex, vertex, self.__end)
        painter.drawPath(path)
        angle = path.angleAtPercent(1)

        # draw arrow head
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(-self.__triangleSize, -self.__triangleSize)
        path.lineTo(self.__triangleSize, -self.__triangleSize)
        path.lineTo(0, 0)

        painter.save()
        painter.translate(self.__end)
        painter.rotate(270 - angle)
        painter.fillPath(path, QBrush(self.__color))
        painter.restore()
