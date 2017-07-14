from PySide import QtCore, QtGui
from PySide.phonon import Phonon
from hilink.settings import SettingsDialog


class ModemIndicator(QtGui.QSystemTrayIcon):
    """Simple tray indicator"""

    # store last message count
    _lastMessageCount = 0

    # status, messages, params
    _status = [""] * 3

    def __init__(self, modem):
        super(ModemIndicator, self).__init__()
        self._modem = modem
        self.signalLevelChanged(0)
        menu = self.createMenu()
        self.setContextMenu(menu)

        self.player = Phonon.createPlayer(Phonon.MusicCategory)
        self.player.stateChanged.connect(self._playerLog)

    def createMenu(self):
        menu = QtGui.QMenu()

        self.connectAction = menu.addAction("Connect")
        self.connectAction.triggered.connect(self.toggleConnect)
        self.connectAction.setVisible(False)

        self.rebootAction = menu.addAction("Reboot")
        self.rebootAction.triggered.connect(self._modem.reboot)
        self.rebootAction.setVisible(False)

        menu.addSeparator()

        self.settingsAction = menu.addAction("Settings")
        self.settingsAction.triggered.connect(self.showSettingsDialog)

        menu.addSeparator()

        quitAction = QtGui.QAction("Quit", menu)
        quitAction.triggered.connect(self.quit)
        menu.addAction(quitAction)

        return menu

    def showSettingsDialog(self):
        dialog = SettingsDialog(self._modem.ip, self._modem.interval)
        if dialog.exec_() == SettingsDialog.Accepted:
            self._modem.ip = dialog.ip
            self._modem.interval = dialog.interval

    def quit(self):
        self.hide()
        self._modem.finish()

    def toggleConnect(self):
        if self.connectAction.text() == "Connect":
            self._modem.connect_()
        else:
            self._modem.disconnect()

    def signalLevelChanged(self, level):
        iconName = "://images/icon_signal_00.png"
        if level in range(1, 6):
            iconName = "://images/icon_signal_0{}.png".format(level)

        self.setIcon(QtGui.QIcon(iconName))

    def needNotify(self, messageCount):
        if messageCount > 0:
            if messageCount > self._lastMessageCount:
                self._playSound()
            self._status[1] = "New Messages: %d" % messageCount
        else:
            self._status[1] = ""
        self._lastMessageCount = messageCount

    def statusChanged(self, status, operator):
        if status == "No HiLink Detected":
            self.connectAction.setVisible(False)
            self.rebootAction.setVisible(False)
        elif status == "Connected":
            self.connectAction.setVisible(True)
            self.rebootAction.setVisible(True)
            self.connectAction.setText("Disconnect")
        elif status == "Disconnected":
            self.connectAction.setVisible(True)
            self.rebootAction.setVisible(True)
            self.connectAction.setText("Connect")

        if (operator == "No Service" or
                status in ["Connecting", "Disconnecting"]):
            self.connectAction.setVisible(False)
            self.rebootAction.setVisible(True)

        if operator != "":
            self._status[0] = "%s\n%s" % (operator, status)
        else:
            self._status[0] = status

    def signalParamsChanged(self, params):
        tip = []
        for value in params.values():
            tip.append(value)

        self._status[2] = "\n".join(tip)
        self.setToolTip("\n".join(filter(None, self._status)))

    def _playSound(self):
        source = Phonon.MediaSource("://sounds/unread_message.wav")
        self.player.setCurrentSource(source)
        self.player.play()

    def _playerLog(self, newState, oldState):
        if newState == Phonon.ErrorState:
            print(self.player.errorString())
