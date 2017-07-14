from PySide import QtCore, QtGui
from hilink.modem import Modem
from hilink.indicator import ModemIndicator


class Tray(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self, ip, interval):
        super(Tray, self).__init__()
        modemIp, requestInterval = self.loadSettings(ip, interval)
        self.setup(modemIp, requestInterval)

    def loadSettings(self, ip, interval):
        settings = QtCore.QSettings("hilink.conf", QtCore.QSettings.IniFormat, self)
        modemIp = ip or settings.value("general/ip", "192.168.8.1")
        requestInterval = interval or int(settings.value("general/interval", 5))
        return (modemIp, requestInterval)

    def setup(self, ip, interval):
        self._monitorThread = QtCore.QThread()
        self._modem = Modem(ip, interval)
        self._modem.moveToThread(self._monitorThread)

        self._modem.finished.connect(self._monitorThread.quit)
        self._monitorThread.finished.connect(self.quit)
        self._monitorThread.started.connect(self._modem.monitor)

        self._trayIndicator = ModemIndicator(self._modem)
        self._modem.levelChanged.connect(
            self._trayIndicator.signalLevelChanged, QtCore.Qt.QueuedConnection)
        self._modem.statusChanged.connect(
            self._trayIndicator.statusChanged, QtCore.Qt.QueuedConnection)
        self._modem.signalParamsChanged.connect(
            self._trayIndicator.signalParamsChanged, QtCore.Qt.QueuedConnection)
        self._modem.unreadMessagesCountChanged.connect(
            self._trayIndicator.needNotify, QtCore.Qt.QueuedConnection)

    def show(self):
        self._trayIndicator.show()
        self._monitorThread.start()

    def quit(self):
        self.saveSettings()
        QtGui.qApp.quit()

    def saveSettings(self):
        settings = QtCore.QSettings("hilink.conf", QtCore.QSettings.IniFormat, self)
        settings.setValue("general/ip", self._modem.ip)
        settings.setValue("general/interval", self._modem.interval)
