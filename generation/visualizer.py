""" Automatically generated documentation for Visualizer """
import logging

from PyQt5.QtCore import Qt
from PySide.QtGui import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout


class EventWidget(QLabel):
    def __init__(self, event, width, parent=None):
        super().__init__(parent)
        self.eventType = event

        self.setFixedHeight(40)
        self.setText(str(event.getEventType()))
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        logging.debug("EventWidget clicked")

    def __eq__(self, other):
        if (not isinstance(EventWidget)):
            return False
        return other.eventType == self.eventType

    def __hash__(self):
        return hash(self.eventType)


class SequenceWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sequence = None
        self.setStyleSheet("border: 1px solid black")
        self.layout = QHBoxLayout()
        self.layout.setSpacing(1)
        self.layout.setAlignment(Qt.AlignBottom)
        self.setLayout(self.layout)
        self.eventWidgets = {}

    def paint(self):
        width = self.geometry().width()
        eventWidth = width // self.sequence.getLength() - 1

        for i in range(0, self.sequence.getLength()):
            event = self.sequence.getEvent(i)
            eventWidget = EventWidget(event, eventWidth)
            self.layout.addWidget(eventWidget)
            self.eventWidgets[event] = eventWidget

    def paintCorrelations(self):
        for event, widget in self.eventWidgets.items():
            response = event.getTriggered()

            if (response is None or response.getTimestamp() == -1):
                continue

            triggeredWidget = self.eventWidgets[event.getTriggered()]

            startPos = widget.pos()
            endPos = triggeredWidget.pos()

            logging.debug("Drawing correlation between {}({}) and {}({})".format(event, startPos, response, endPos))

    def setSequence(self, sequence):
        self.sequence = sequence


class Visualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sequenceWidget = None
        self.layout = None
        self.initGui()

    def initGui(self):
        self.setGeometry(100, 300, 1200, 250)

        widget = QWidget()

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

        self.sequenceWidget = SequenceWidget()
        self.layout.addWidget(self.sequenceWidget, 0, 0)

        self.setCentralWidget(widget)

    def setSequence(self, sequence):
        self.sequenceWidget.setSequence(sequence)
        self.sequenceWidget.paint()
