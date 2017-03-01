import sys

import matplotlib.pyplot as plt
import numpy as np
from PySide.QtCore import QPoint, QRectF
from PySide.QtGui import QBrush, QColor, QFont, QFontMetrics, QGraphicsItem, QPainter, QPainterPath, QPen

from core.distribution import KdeDistribution, NormalDistribution, SingularKernel


class EventWidget(QGraphicsItem):
    def __init__(self, event, pos, highLight=False, size=20, labelBelow=False):
        super().__init__()
        self._eventType = event
        self.__highLight = highLight
        self.__pos = pos
        self.__size = size
        self.__labelBelow = labelBelow
        self.__rect = QRectF(self.__pos.x(), self.__pos.y(), self.__size, self.__size)

        self.setToolTip(event.eventType)

    def boundingRect(self):
        return self.__rect

    def paint(self, painter: QPainter, option, widget):
        size = self.__getTextSize()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.setBrush(QBrush(QColor(225, 225, 232)))
        if (self.__highLight):
            painter.setBrush(QBrush(QColor(92, 184, 92)))

        painter.drawEllipse(self.boundingRect())
        if (self.__labelBelow):
            painter.drawText((self.__pos.x() + self.__size // 2) - size[0] // 2,
                             self.__pos.y() + self.__size + size[1],
                             self._eventType.getExternalRepresentation())
        else:
            painter.drawText(self.__pos.x() + (self.__size - size[0]) // 2,
                             self.__pos.y() + (self.__size + size[1]) // 2,
                             self._eventType.getExternalRepresentation() if
                             len(self._eventType.getExternalRepresentation()) <= 3 else '!')

    def __getTextSize(self):
        font = QFont()
        metric = QFontMetrics(font)
        width = metric.width(self._eventType.getExternalRepresentation() if
                             len(self._eventType.getExternalRepresentation()) <= 3 else '!')
        height = metric.height()
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

        vertex = QPoint(self.__start.x() + (self.__end.x() - self.__start.x()) / 2, self.__start.y() - self.__arcOffset)
        self.__rect = QRectF(QPoint(min(start.x(), end.x()) - self.__triangleSize,
                                    min(start.y(), end.y(), vertex.y()) - self.__triangleSize),
                             QPoint(max(start.x(), end.x()) + self.__triangleSize,
                                    max(start.y(), end.y(), vertex.y()) + self.__triangleSize))

    def boundingRect(self):
        return self.__rect

    def shape(self, *args, **kwargs):
        if (self.__arcOffset != 0):
            return super().shape()

        direction = self.__end - self.__start
        perpendicular = QPoint(-direction.y(), direction.x())
        perpendicular = (perpendicular / np.linalg.norm(np.array([perpendicular.x(), perpendicular.y()]))) * 2

        path = QPainterPath()
        path.moveTo(self.__start + perpendicular)
        path.lineTo(self.__end + perpendicular)
        path.lineTo(self.__end - perpendicular)
        path.lineTo(self.__start - perpendicular)

        return path

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


CORRECT = 'correct'
LP = 'lp'
ICE = 'ice'
LAGEM = 'lagEm'


# noinspection PyProtectedMember,PyUnresolvedReferences
def plotDistributions(data, title=None, limit=None):
    correct = None
    if (CORRECT in data and data[CORRECT] is not None):
        if (not isinstance(data[CORRECT], list)):
            correct = data[CORRECT]
        elif (len(data[CORRECT]) > 0):
            correct = KdeDistribution(data[CORRECT])
            if (isinstance(correct._KdeDistribution__kernel, SingularKernel)):
                correct.__kernel.maxValue = 500

    lp = None
    if (LP in data and data[LP] is not None):
        lp = data[LP]
        if (isinstance(data[LP], list) and len(data[LP]) > 0):
            lp = KdeDistribution(data[LP])
        if (isinstance(lp._KdeDistribution__kernel, SingularKernel)):
            lp._KdeDistribution__kernel.maxValue = 500

    ice = None
    if (ICE in data and data[ICE] is not None):
        ice = data[ICE]
        if (isinstance(data[ICE], list) and len(data[ICE]) > 0):
            ice = KdeDistribution(data[ICE])
        if (isinstance(ice._KdeDistribution__kernel, SingularKernel)):
            ice._KdeDistribution__kernel.maxValue = 500

    lagEM = None
    if (LAGEM in data and data[LAGEM] is not None):
        lagEM = data[LAGEM]
        if (isinstance(data[LAGEM], list) and len(data[LAGEM]) > 0):
            lagEM = NormalDistribution(data[LAGEM][0], data[LAGEM][1])

    borders1 = correct.getCompleteInterval() if (correct is not None) else [sys.maxsize, -sys.maxsize]
    borders2 = lp.getCompleteInterval() if (lp is not None) else [sys.maxsize, -sys.maxsize]
    borders3 = ice.getCompleteInterval() if (ice is not None) else [sys.maxsize, -sys.maxsize]
    borders4 = lagEM.getCompleteInterval() if (lagEM is not None) else [sys.maxsize, -sys.maxsize]

    lower = min(borders1[0], borders2[0], borders3[0], borders4[0])
    upper = max(borders1[1], borders2[1], borders3[1], borders4[1])
    x = np.linspace(lower - min(100, abs(lower / 5)), upper + min(100, abs(upper / 5)), 5000)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Time Lag")
    ax.set_ylabel("Probability Density")
    if (title is not None):
        fig.canvas.set_window_title(title)
    if (limit is not None):
        ax.set_ylim([0, limit])

    lw = 1.2
    if (correct is not None):
        y1 = correct.getPDFValue(x)
        ax.plot(x, y1, "r", label="True distribution", linewidth=lw)

    if (lp is not None):
        y2 = lp.getPDFValue(x)
        ax.plot(x, y2, "g", label="LpMatcher", linewidth=lw)

    if (ice is not None):
        y3 = ice.getPDFValue(x)
        ax.plot(x, y3, "c", label="ICE", linewidth=lw)

    if (lagEM is not None):
        y4 = lagEM.getPDFValue(x)
        ax.plot(x, y4, 'b', label='lagEM', linewidth=lw)

    plt.legend(loc='best')
