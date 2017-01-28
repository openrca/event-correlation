import math

import networkx as nx
import numpy as np
from PySide.QtCore import QPoint, Signal, Qt
from PySide.QtGui import QGraphicsScene, QGraphicsView, QHBoxLayout, QWidget, QSizePolicy, QVBoxLayout, QSlider

from core.bayesianNetwork import BayesianNetwork
from core.event import Event
from core.rule import Rule
from visualization import EventWidget, ArrowWidget
from visualization.details import DetailsContainer


class ResponsiveArrowWidget(ArrowWidget):
    def __init__(self, start, end, color=0, parent=None):
        super().__init__(start, end, color=color)
        self._callbackParam = None
        self.__parent = parent

    def mouseDoubleClickEvent(self, event):
        if (self.__parent is not None):
            self.__parent.detailsSignal.emit(self._callbackParam)


class DependenciesView(QWidget):
    __paintSeq = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dependency Graph')
        self.__mutualInformation = np.zeros(1)

        layout = QHBoxLayout()
        self.setLayout(layout)

        layoutLeft = QVBoxLayout()
        self.__tree = DependencyTree(self)
        self.__paintSeq.connect(self.__tree.paint)
        self.__view = QGraphicsView()
        self.__view.setScene(self.__tree)
        layoutLeft.addWidget(self.__view)

        self.__slider = QSlider(Qt.Orientation.Horizontal)
        self.__slider.setRange(0, 100)
        self.__slider.setSliderPosition(100)
        self.__slider.setTickInterval(25)
        self.__slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        # noinspection PyUnresolvedReferences
        self.__slider.valueChanged.connect(self.__sensitivityChanged)
        layoutLeft.addWidget(self.__slider)

        containerLeft = QWidget()
        policyLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policyLeft.setHorizontalStretch(2)
        containerLeft.setSizePolicy(policyLeft)
        containerLeft.setLayout(layoutLeft)
        layout.addWidget(containerLeft)

        self.__details = DetailsContainer(showPlot=True, showAssignments=False)
        policyRight = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policyRight.setHorizontalStretch(1)
        self.__details.setSizePolicy(policyRight)
        layout.addWidget(self.__details, 0, 2)

    def setData(self, root, sequence):
        self.__mutualInformation = np.zeros(len(sequence.calculatedRules))
        for index, rule in enumerate(sequence.calculatedRules):
            self.__mutualInformation[index] = rule.data["Mutual Information"] if "Mutual Information" in rule.data \
                else None
        self.__sensitivityChanged(redraw=False)
        self.__tree.setData(root, sequence)

    def setDetails(self, sequence, rule):
        self.__details.setData(sequence, rule)

    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        self.__view.items().clear()
        self.__tree.paint()

    def show(self, *args, **kwargs):
        super().show(*args, **kwargs)
        self.__view.items().clear()
        self.__tree.paint()

    def __sensitivityChanged(self, redraw=True):
        if (self.__mutualInformation is None):
            return

        epsilon = self.__slider.value() / 100
        percentile25 = np.percentile(self.__mutualInformation, 25)
        percentile75 = np.percentile(self.__mutualInformation, 75)

        threshold = (percentile25 - (0.5 + epsilon) * (percentile75 - percentile25)) * 2
        self.__tree._threshold = threshold
        if (redraw):
            self.__view.items().clear()
            self.__paintSeq.emit()


class DependencyTree(QGraphicsScene):
    detailsSignal = Signal(Rule)

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__offset = [50, 50]
        self.__eventSize = 20
        self.__parent = parent
        self.__root = None
        self.__sequence = None
        self.__bn = None
        self.__positions = None
        self._threshold = 0
        self.detailsSignal.connect(self.__showDetails)

    def setData(self, root, sequence):
        if (sequence.calculatedRules is None):
            return
        self.__root = root
        self.__sequence = sequence

        self.__bn = BayesianNetwork(sequence)
        if (self.__root is None):
            self.__bn.createCompleteGraph()
        else:
            self.__bn.createGraph(self.__root)
        self.__bn.learnStructure()
        self.__normalizePositions(nx.nx_pydot.graphviz_layout(self.__bn.graph, prog='dot'))

    def __normalizePositions(self, positions):
        self.__positions = {}
        pos = np.array(list(positions.values()))
        x = pos[:, 0].max()
        y = pos[:, 1].max()

        for key, value in positions.items():
            value = list(value)
            value[0] /= x
            value[1] /= y
            self.__positions[key] = value

    def paint(self):
        self.clear()
        size = [self.__parent.width() * 0.5, self.__parent.height() * 0.8]

        for start, end in self.__bn.graph.edges():
            startPoint = self.__pointToPlane(self.__positions[start], size, center=True)
            endPoint = self.__clipPointToCircle(startPoint,
                                                self.__pointToPlane(self.__positions[end], size, center=True))

            rule = self.__sequence.getCalculatedRule(start, end)
            if (rule is None):
                rule = self.__sequence.getCalculatedRule(end, start)
            if (rule is not None):
                color = 200 if (rule.data["Mutual Information"] < self._threshold) else 0
                widget = ResponsiveArrowWidget(startPoint, endPoint, color=color, parent=self)
                widget._callbackParam = self.__sequence.getCalculatedRule(start, end)
                self.addItem(widget)

        for key, value in self.__positions.items():
            point = self.__pointToPlane(value, size)
            widget = EventWidget(Event(key), point, self.__root is not None and key in self.__root, labelBelow=True)
            widget.eventType = key
            self.addItem(widget)

    def __pointToPlane(self, point, size, center=False):
        point = QPoint(point[0] * size[0], point[1] * size[1])
        if (center):
            point = QPoint(point.x() + self.__eventSize // 2, point.y() + self.__eventSize // 2)
        return point

    def __clipPointToCircle(self, start, end):
        length = math.sqrt((start.x() - end.x()) ** 2 + (start.y() - end.y()) ** 2)
        percentage = (length - self.__eventSize // 2) / length

        distanceX = (end.x() - start.x()) * percentage
        distanceY = (end.y() - start.y()) * percentage

        return QPoint(start.x() + distanceX, start.y() + distanceY)

    def __showDetails(self, rule):
        if (rule is None):
            return
        self.__parent.setDetails(self.__sequence, rule)
