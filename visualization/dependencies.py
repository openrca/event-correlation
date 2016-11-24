import math

import networkx as nx
import numpy as np
from PySide.QtCore import QPoint, Signal
from PySide.QtGui import QGraphicsScene, QGraphicsView, QHBoxLayout, QWidget, QSizePolicy

from core.event import Event
from core.rule import Rule
from visualization import EventWidget, ArrowWidget
from visualization.details import DetailsContainer


class ResponsiveArrowWidget(ArrowWidget):
    def __init__(self, start, end, parent=None):
        super().__init__(start, end)
        self._callbackParam = None
        self.__parent = parent

    def mouseDoubleClickEvent(self, event):
        if (self.__parent is not None):
            self.__parent.detailsSignal.emit(self._callbackParam)


class DependenciesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dependency Graph')

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.__tree = DependencyTree(self)
        self.__view = QGraphicsView()
        self.__view.setScene(self.__tree)
        policyLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policyLeft.setHorizontalStretch(2)
        self.__view.setSizePolicy(policyLeft)
        layout.addWidget(self.__view)

        self.__details = DetailsContainer(showPlot=True, showAssignments=False)
        policyRight = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policyRight.setHorizontalStretch(1)
        self.__details.setSizePolicy(policyRight)
        layout.addWidget(self.__details, 0, 2)

    def setData(self, root, sequence):
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


class DependencyTree(QGraphicsScene):
    detailsSignal = Signal(Rule)

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__offset = [50, 50]
        self.__eventSize = 20
        self.__parent = parent
        self.__root = None
        self.__sequence = None
        self.__graph = None
        self.__positions = None
        self.detailsSignal.connect(self.__showDetails)

    def setData(self, root, sequence):
        if (sequence.calculatedRules is None):
            return
        self.__root = root
        self.__sequence = sequence

        if (self.__root is None):
            self.__graph = self.__createCompleteGraph(self.__sequence.calculatedRules)
        else:
            self.__graph = self.__createGraph(root)
        self.__positions = nx.fruchterman_reingold_layout(self.__graph)
        self.__normalizePositions()

    @staticmethod
    def __createCompleteGraph(rules):
        graph = nx.Graph()
        for rule in rules:
            graph.add_node(rule.trigger)
            graph.add_node(rule.response)
        for rule in rules:
            graph.add_edge(rule.trigger, rule.response)
        return graph

    def __createGraph(self, root):
        tree = self.__createTreeFromRules(self.__sequence.calculatedRules)
        edges = set()
        processed = set()

        graph = nx.Graph()
        elements = [root]
        while len(elements) > 0:
            newElements = []
            for element in elements:
                if (element in processed):
                    continue
                processed.add(element)

                for event in tree[element]:
                    graph.add_node(event)
                    edges.add((element, event))
                    newElements.append(event)
            elements = set(newElements)

        graph.add_edges_from(edges)
        return graph

    @staticmethod
    def __createTreeFromRules(rules):
        tree = {}
        for rule in rules:
            tree.setdefault(rule.trigger, []).append(rule.response)
        for rule in rules:
            tree.setdefault(rule.response, []).append(rule.trigger)
        return tree

    def __normalizePositions(self):
        pos = np.array(list(self.__positions.values()))
        x = pos[:, 0].max()
        y = pos[:, 1].max()

        for key, value in self.__positions.items():
            value[0] /= x
            value[1] /= y

    def paint(self):
        self.clear()
        size = [self.__parent.width() * 0.5, self.__parent.height() * 0.8]

        for start, end in self.__graph.edges():
            startPoint = self.__pointToPlane(self.__positions[start], size, center=True)
            endPoint = self.__clipPointToCircle(startPoint,
                                                self.__pointToPlane(self.__positions[end], size, center=True))

            rule = self.__sequence.getCalculatedRule(start, end)
            if (rule is not None):
                widget = ResponsiveArrowWidget(startPoint, endPoint, parent=self)
                widget._callbackParam = self.__sequence.getCalculatedRule(start, end)
                self.addItem(widget)

        for key, value in self.__positions.items():
            point = self.__pointToPlane(value, size)
            widget = EventWidget(Event(key), point, key == self.__root, labelBelow=True)
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
