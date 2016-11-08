import math
import networkx as nx
from PySide.QtCore import QPoint
from PySide.QtGui import QGraphicsScene, QGraphicsView, QVBoxLayout, QWidget

from core.event import Event
from visualization import EventWidget, ArrowWidget


class DependenciesView(QWidget):
    def __init__(self):
        super().__init__()
        self.__root = None
        self.__rules = None
        self.setWindowTitle('Dependency Graph')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.__widget = DependencyTree(self)
        self.__view = QGraphicsView()
        self.__view.setScene(self.__widget)
        layout.addWidget(self.__view)

    def setData(self, rules, root):
        self.__rules = rules
        self.__root = root

    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        self.__view.items().clear()
        self.__widget.paint(self.__root, self.__rules)

    def show(self, *args, **kwargs):
        super().show(*args, **kwargs)
        self.__view.items().clear()
        self.__widget.paint(self.__root, self.__rules)


class DependencyTree(QGraphicsScene):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__offset = [50, 50]
        self.__eventSize = 20
        self.__parent = parent

    def paint(self, root, rules):
        if (root is None or rules is None):
            return
        self.clear()

        size = [self.__parent.width() - self.__parent.width() // 5,
                self.__parent.height() - self.__parent.height() // 5]
        margin = [self.__parent.width() // 20, self.__parent.height() // 20]

        tree = self.__createTreeFromRules(rules)
        graph = self.__createGraph(root, tree)
        positions = nx.fruchterman_reingold_layout(graph)

        for start, end in graph.edges():
            startPoint = self.__pointToPlane(positions[start], size, margin, center=True)
            endPoint = self.__clipPointToCircle(startPoint,
                                                self.__pointToPlane(positions[end], size, margin, center=True))

            widget = ArrowWidget(startPoint, endPoint, arcOffset=0)
            self.addItem(widget)

        for key, value in positions.items():
            point = self.__pointToPlane(value, size, margin)
            widget = EventWidget(Event(key), point, key == root)
            widget.eventType = key
            self.addItem(widget)

    @staticmethod
    def __createTreeFromRules(rules):
        tree = {}
        for rule in rules:
            tree.setdefault(rule.trigger, []).append(rule.response)
        return tree

    @staticmethod
    def __createGraph(root, tree):
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

    def __pointToPlane(self, point, size, margin, center=False):
        point = QPoint(point[0] * size[0] + margin[0], point[1] * size[1] + margin[1])
        if (center):
            point = QPoint(point.x() + self.__eventSize // 2, point.y() + self.__eventSize // 2)
        return point

    def __clipPointToCircle(self, start, end):
        length = math.sqrt((start.x() - end.x()) ** 2 + (start.y() - end.y()) ** 2)
        percentage = (length - self.__eventSize // 2) / length

        distanceX = (end.x() - start.x()) * percentage
        distanceY = (end.y() - start.y()) * percentage

        return QPoint(start.x() + distanceX, start.y() + distanceY)
