import matplotlib.pyplot as plt
import numpy as np
from PySide import QtGui, QtCore
from PySide.QtGui import QTableWidget, QTableWidgetItem, QWidget, QPushButton
from PySide.QtGui import QVBoxLayout
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from algorithms import RESULT_IDX


# noinspection PyAbstractClass
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self._figure = Figure()
        self._fillFigure()

        super().__init__(self._figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def _fillFigure(self):
        pass


# noinspection PyAbstractClass
class DetailsCanvas(MplCanvas):
    def __init__(self, sequence, rule):
        self.__sequence = sequence
        self.__rule = rule
        super().__init__()

    def _fillFigure(self):
        self._showDistributions(self._figure.add_subplot(121))
        self._showFinalAssignment(self._figure.add_subplot(122))

    def _showDistributions(self, ax):
        estimatedDist = self.__rule.distributionResponse
        trueDist = self.__sequence.getBaseDistribution(self.__rule)

        borders1 = estimatedDist.getCompleteInterval()
        borders2 = trueDist.getCompleteInterval() if (trueDist is not None) else estimatedDist.getCompleteInterval()

        lower = min(borders1[0], borders2[0])
        upper = max(borders1[1], borders2[1])
        x = np.linspace(lower - abs(lower / 10), upper + abs(upper / 10), 5000)
        y1 = estimatedDist.getPDFValue(x)
        ax.plot(x, y1, "b", label="Estimated distribution")

        if (trueDist is not None):
            y2 = trueDist.getPDFValue(x)
            ax.plot(x, y2, "r", label="True distribution")

            tmp = np.zeros(len(y1))
            for i in range(len(y1)):
                tmp[i] = min(y1[i], y2[i])
            ax.fill_between(x, 0, tmp, facecolor="#E8E8E8", edgecolor="#E8E8E8")

        ax.legend()
        ax.set_xlabel("Time Lag")
        ax.set_ylabel("Probability")

    def _showFinalAssignment(self, ax):
        if (RESULT_IDX not in self.__rule.data):
            return

        trigger = self.__rule.trigger
        response = self.__rule.response
        idx = np.array(self.__rule.data[RESULT_IDX])

        missingTrigger = self.__sequence.getMissingIdx(trigger)
        missingResponse = self.__sequence.getMissingIdx(response)

        i = np.array(idx, copy=True)
        for j in range(idx.shape[0]):
            i[j][0] += len(np.where(missingTrigger <= j)[0])
            i[j][1] += len(np.where(missingResponse <= j)[0])

        ax.plot(i[:, 0], i[:, 1], "ro", label="Assignment")
        ax.plot(np.arange(i.max() + 1), np.arange(i.max() + 1), "-", label="Theoretically optimal")
        if (len(missingTrigger) > 0):
            ax.plot(missingTrigger, [0.5] * len(missingTrigger), "rx", label="Missing " + trigger)
        if (len(missingResponse) > 0):
            ax.plot([0.5] * len(missingResponse), missingResponse, "yx", label="Missing " + response)
        ax.set_xlabel("Event " + trigger)
        ax.set_ylabel("Event " + response)
        ax.legend(loc="upper left")


class DetailsTable(QTableWidget):
    def __init__(self, data):
        super().__init__()
        self.__data = data
        self.__fillTable()
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def __fillTable(self):
        self.setColumnCount(2)
        self.setRowCount(len(self.__data))

        for index, (key, value) in enumerate(self.__data.items()):
            leftItem = QTableWidgetItem(str(key))
            rightItem = QTableWidgetItem(str(value))
            self.setItem(index, 0, leftItem)
            self.setItem(index, 1, rightItem)


class DetailsContainer(QWidget):
    def __init__(self, sequence, rule):
        super().__init__()

        self.__canvas = DetailsCanvas(sequence, rule)
        self.__details = DetailsTable(rule.data)

        self.__externalFiguresButton = QPushButton('External Figures')
        # noinspection PyUnresolvedReferences
        self.__externalFiguresButton.clicked.connect(self.__externalFigures)

        layout = QVBoxLayout()
        layout.addWidget(self.__canvas)
        layout.addWidget(self.__details)
        layout.addWidget(self.__externalFiguresButton)

        self.setLayout(layout)

    def __externalFigures(self):
        fig, ax = plt.subplots(1, 1)
        # noinspection PyProtectedMember
        self.__canvas._showDistributions(ax)
        fig, ax = plt.subplots(1, 1)
        # noinspection PyProtectedMember
        self.__canvas._showFinalAssignment(ax)
        plt.show()
