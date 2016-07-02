import sys
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from PySide.QtGui import QApplication

from visualization.visualizer import Visualizer


def showAllDistributions(sequence):
    if (len(sequence.rules) != 0 and len(sequence.calculatedRules) != 0):
        for rule in sequence.rules:
            calculatedRule = sequence.getCalculatedRule(rule.trigger, rule.response)
            if (calculatedRule is not None):
                showDistributions(calculatedRule.distribution, rule.distribution)


def showDistributions(estimatedDist, trueDist, visualizeOverlap=True, axes=None):
    if (axes is None):
        ax = plt.gca()
    else:
        ax = axes

    if (trueDist is None):
        borders2 = estimatedDist.getCompleteInterval()
    else:
        borders2 = trueDist.getCompleteInterval()
    borders1 = estimatedDist.getCompleteInterval()
    x = np.linspace(min(borders1[0], borders2[0]) - 1, max(borders1[1], borders2[1]) + 1, 500)

    y1 = estimatedDist.getPDFValue(x)
    ax.plot(x, y1, "b", label="Estimated distribution")

    if (trueDist is not None):
        y2 = trueDist.getPDFValue(x)
        ax.plot(x, y2, "r", label="True distribution")
    ax.legend()

    if (visualizeOverlap and trueDist is not None):
        y = np.zeros(len(y1))
        for i in range(len(y1)):
            y[i] = min(y1[i], y2[i])
        ax.fill_between(x, 0, y, facecolor="#E8E8E8", edgecolor="#E8E8E8")

    if (axes is None):
        plt.show()
        sleep(1)


def showFinalAssignment(sequence, eventA, eventB, idx, axes=None):
    if (axes is None):
        ax = plt.gca()
    else:
        ax = axes

    missingA = sequence.getMissingIdx(eventA)
    missingB = sequence.getMissingIdx(eventB)

    i = np.array(idx, copy=True)
    for j in range(idx.shape[0]):
        i[j][0] += len(np.where(missingA <= j)[0])
        i[j][1] += len(np.where(missingB <= j)[0])

    ax.plot(i[:, 0], i[:, 1], "ro", label="Assignment")
    ax.plot(np.arange(i.max() + 1), np.arange(i.max() + 1), "-", label="Theoretically optimal")
    if (len(missingA) > 0):
        ax.plot(missingA, [0.5] * len(missingA), "rx", label="Missing " + eventA)
    if (len(missingB) > 0):
        ax.plot([0.5] * len(missingB), missingB, "yx", label="Missing " + eventB)
    ax.set_xlabel("Event " + eventA)
    ax.set_ylabel("Event " + eventB)
    ax.legend(loc="upper left")
    if (axes is None):
        plt.show()
        sleep(1)


def showResult(sequence, eventA, eventB, idx, trueDist, estimatedDist):
    if (idx is None):
        showDistributions(estimatedDist, trueDist)
        return

    f, axes = plt.subplots(1, 2)
    showDistributions(estimatedDist, trueDist, axes=axes[0])
    showFinalAssignment(sequence, eventA, eventB, idx, axes=axes[1])
    plt.show()
    sleep(1)


def showVisualizer(sequence=None):
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    if (sequence is not None):
        v.setSequence(sequence)

    sys.exit(app.exec_())
