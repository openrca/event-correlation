import sys

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


def showDistributions(estimatedDist, trueDist):
    borders1 = estimatedDist.dist.interval(0.99)
    borders2 = trueDist.dist.interval(0.99)
    x = np.linspace(min(borders1[0], borders2[0]), max(borders1[1], borders2[1]), 500)
    plt.plot(x, estimatedDist.dist.pdf(x), "b", label="Estimated distribution")
    plt.plot(x, trueDist.dist.pdf(x), "r", label="True distribution")
    plt.legend()
    plt.show()


def getAreaBetweenDistributions(dist1, dist2):
    borders1 = dist1.dist.interval(0.99)
    borders2 = dist2.dist.interval(0.99)
    x = np.linspace(min(borders1[0], borders2[0]), max(borders1[1], borders2[1]), 2000)
    y = np.amin(np.array([dist1.dist.pdf(x), dist2.dist.pdf(x)]), axis=0)
    print("Area between pdf curves: " + str(scipy.integrate.simps(y, x)))


def showVisualizer(sequence=None):
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    if (sequence is not None):
        v.setSequence(sequence)

    sys.exit(app.exec_())
