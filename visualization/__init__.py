import sys
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate
from PySide.QtGui import QApplication

from visualization.visualizer import Visualizer


def showAllDistributions(sequence):
    if (len(sequence.rules) != 0 and len(sequence.calculatedRules) != 0):
        for rule in sequence.rules:
            calculatedRule = sequence.getCalculatedRule(rule.trigger, rule.response)
            if (calculatedRule is not None):
                showDistributions(calculatedRule.distribution, rule.distribution)


def showDistributions(estimatedDist, trueDist, visualizeOverlap=True):
    borders1 = estimatedDist.getCompleteInterval()
    borders2 = trueDist.getCompleteInterval()
    x = np.linspace(min(borders1[0], borders2[0]) - 1, max(borders1[1], borders2[1]) + 1, 500)
    y1 = estimatedDist.getPDFValue(x)
    y2 = trueDist.getPDFValue(x)

    plt.plot(x, y1, "b", label="Estimated distribution")
    plt.plot(x, y2, "r", label="True distribution")
    plt.legend()

    if (visualizeOverlap):
        ax = plt.gca()
        y = np.zeros(len(y1))
        for i in range(len(y1)):
            y[i] = min(y1[i], y2[i])
        ax.fill_between(x, 0, y, facecolor="#E8E8E8", edgecolor="#E8E8E8")

    plt.show()
    sleep(1)


def getAreaBetweenDistributions(dist1, dist2):
    borders1 = dist1.getCompleteInterval()
    borders2 = dist2.getCompleteInterval()
    x = np.linspace(min(borders1[0], borders2[0]), max(borders1[1], borders2[1]), 2000)
    y = np.amin(np.array([dist1.getPDFValue(x), dist2.getPDFValue(x)]), axis=0)
    return scipy.integrate.simps(y, x)


def showVisualizer(sequence=None):
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    if (sequence is not None):
        v.setSequence(sequence)

    sys.exit(app.exec_())
