from PySide import QtGui


class SettingsDialog(QtGui.QDialog):
    def __init__(self, ip, interval):
        super(SettingsDialog, self).__init__()
        self._ip = ip
        self._interval = interval

        self.setupUi()

    @property
    def ip(self):
        return self._ip

    @property
    def interval(self):
        return self._interval

    def setupUi(self):
        self.setWindowTitle("Settings")
        layout = QtGui.QFormLayout()

        self._ipField = QtGui.QLineEdit()
        self._ipField.setText(self.ip)
        layout.addRow("IP:", self._ipField)

        self._intervalField = QtGui.QLineEdit()
        self._intervalField.setText(str(self.interval))
        layout.addRow("Interval:", self._intervalField)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.onAccept)
        buttonBox.rejected.connect(self.reject)
        layout.addRow(buttonBox)

        self.setLayout(layout)

    def onAccept(self):
        self._ip = self._ipField.text()
        self._interval = int(self._intervalField.text())
        self.accept()
