import json

from PySide2.QtWidgets import QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from core.bayesianNetwork import Evidence


class Query(QWidget):
    def __init__(self, bn):
        super().__init__()
        self.__bn = bn
        self.__variable = QLineEdit()
        self.__evidence = QTextEdit()
        self.__submit = QPushButton('Query')
        # noinspection PyUnresolvedReferences
        self.__submit.clicked.connect(self.__submitQuery)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Variable'))
        layout.addWidget(self.__variable)
        layout.addWidget(QLabel('Evidence'))
        layout.addWidget(self.__evidence)
        layout.addWidget(self.__submit)
        self.setLayout(layout)

    def __submitQuery(self):
        variable = str(self.__variable.text())
        evidenceInput = str(self.__evidence.toPlainText())
        evidenceInput = json.loads(evidenceInput)

        evidence = []
        for key, value in evidenceInput.items():
            evidence.append(Evidence(key, bool(value)))

        res = self.__bn.query(variable, evidence)
        print(res)
        # QMessageBox.information(self, 'Result', str(res))
