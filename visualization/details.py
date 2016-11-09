import matplotlib.pyplot as plt
import numpy as np
from PySide import QtGui, QtCore
from PySide.QtGui import QTableWidget, QTableWidgetItem, QWidget, QPushButton, QLabel
from PySide.QtGui import QVBoxLayout
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from algorithms import RESULT_IDX


# noinspection PyAbstractClass
class DetailsCanvas(FigureCanvas):
    def __init__(self, showPlot=True, showAssignments=True, parent=None):
        self._figure = Figure()
        super().__init__(self._figure)
        self.setParent(parent)

        if (showPlot and showAssignments):
            self.__axLeft = self._figure.add_subplot(121)
            self.__axRight = self._figure.add_subplot(122)
        elif (showPlot):
            self.__axLeft = self._figure.add_subplot(111)
            self.__axLeft = self._figure.add_subplot(111)
            self.__axRight = None
        elif (showAssignments):
            self.__axRight = self._figure.add_subplot(111)
            self.__axLeft = None

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def setData(self, sequence, rule):
        if (self.__axLeft is not None):
            self.__axLeft.clear()
            self._showDistributions(self.__axLeft, rule, sequence)
        if (self.__axRight is not None):
            self.__axRight.clear()
            self._showFinalAssignment(self.__axRight, rule, sequence)
        self._figure.canvas.draw()

    @staticmethod
    def _showDistributions(ax, rule, sequence):
        estimatedDist = rule.distributionResponse
        trueDist = sequence.getBaseDistribution(rule)

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

    @staticmethod
    def _showFinalAssignment(ax, rule, sequence):
        if (RESULT_IDX not in rule.data):
            return

        trigger = rule.trigger
        response = rule.response
        idx = np.array(rule.data[RESULT_IDX])

        missingTrigger = sequence.getMissingIdx(trigger)
        missingResponse = sequence.getMissingIdx(response)

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
    def __init__(self):
        super().__init__()
        self.resizeColumnsToContents()
        self.setColumnCount(2)
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def setData(self, data):
        for i in reversed(range(self.rowCount())):
            self.removeRow(i)
        self.setRowCount(len(data))

        for index, (key, value) in enumerate(data.items()):
            leftItem = QTableWidgetItem(str(key))
            rightItem = QTableWidgetItem(str(value))
            self.setItem(index, 0, leftItem)
            self.setItem(index, 1, rightItem)


class DetailsContainer(QWidget):
    def __init__(self, showPlot=True, showAssignments=True):
        super().__init__()

        self.__canvas = DetailsCanvas(showPlot=showPlot, showAssignments=showAssignments)
        self.__label = QLabel('Rule')
        self.__details = DetailsTable()

        self.__sequence = None
        self.__rule = None

        self.__externalFiguresButton = QPushButton('External Figures')
        # noinspection PyUnresolvedReferences
        self.__externalFiguresButton.clicked.connect(self.__externalFigures)

        layout = QVBoxLayout()
        layout.addWidget(self.__canvas)
        layout.addWidget(self.__label)
        layout.addWidget(self.__details)
        layout.addWidget(self.__externalFiguresButton)

        self.setLayout(layout)

    def setData(self, sequence, rule):
        if (sequence is None or rule is None):
            return
        self.__sequence = sequence
        self.__rule = rule
        self.__canvas.setData(sequence, rule)
        self.__label.setText('{} -> {}'.format(rule.trigger, rule.response))
        self.__details.setData(rule.data)

    def __externalFigures(self):
        fig, ax = plt.subplots(1, 1)
        # noinspection PyProtectedMember
        self.__canvas._showDistributions(ax, self.__rule, self.__sequence)
        fig, ax = plt.subplots(1, 1)
        # noinspection PyProtectedMember
        self.__canvas._showFinalAssignment(ax, self.__rule, self.__sequence)
        plt.show()
