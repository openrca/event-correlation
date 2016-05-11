import sys

import matplotlib.pyplot as plt
import numpy as np
from PySide.QtGui import QApplication

from visualization.visualizer import Visualizer


def showDistributions(dist1, dist2):
    borders1 = dist1.dist.interval(0.99)
    borders2 = dist2.dist.interval(0.99)
    x = np.linspace(min(borders1[0], borders2[0]), max(borders1[1], borders2[1]), 500)
    plt.plot(x, dist1.dist.pdf(x), "b", label="Estimated distribution")
    plt.plot(x, dist2.dist.pdf(x), "r", label="True distribution")
    plt.legend()
    plt.show()


def showVisualizer(sequence=None):
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    if (sequence is not None):
        v.setSequence(sequence)

    sys.exit(app.exec_())
