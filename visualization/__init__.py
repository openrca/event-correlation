import sys

from PySide.QtGui import QApplication

from visualization.visualizer import Visualizer


def showVisualizer(sequence=None):
    app = QApplication(sys.argv)
    v = Visualizer()
    v.show()
    if (sequence is not None):
        v.setSequence(sequence)

    sys.exit(app.exec_())
