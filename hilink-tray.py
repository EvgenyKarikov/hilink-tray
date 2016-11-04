#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright: 2016, Wasylews
# Author: Wasylews
# License: MIT

from __future__ import print_function
import sys
import signal
import argparse
from PySide import QtCore, QtGui
from PySide.phonon import Phonon
from hilink.modem import Modem

# load resources based on interpreter version
if sys.hexversion >= 0x3000000:
    import hilink.res3_rc
else:
    import hilink.res_rc


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

        self.connectAction = QtGui.QAction("Connect", menu)
        self.connectAction.triggered.connect(self.toggleConnect)
        self.connectAction.setVisible(False)
        menu.addAction(self.connectAction)

        self.rebootAction = QtGui.QAction("Reboot", menu)
        self.rebootAction.triggered.connect(self._modem.reboot)
        self.rebootAction.setVisible(False)
        menu.addAction(self.rebootAction)

        menu.addSeparator()

        quitAction = QtGui.QAction("Quit", menu)
        quitAction.triggered.connect(self.quit)
        menu.addAction(quitAction)

        return menu

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
            self._status[1] = "New messages: %d" % messageCount
        else:
            self._status[1] = ""
        self._lastMessageCount = messageCount

    def statusChanged(self, status, operator):
        if status == "Modem offline":
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

        if (operator == "No service" or
                status in ["Connecting...", "Disconnecting..."]):
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


def main(ip):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)

    monitorThread = QtCore.QThread()
    modem = Modem(ip)
    modem.moveToThread(monitorThread)

    modem.finished.connect(monitorThread.quit)
    monitorThread.finished.connect(app.quit)

    timer = QtCore.QTimer()
    timer.moveToThread(monitorThread)

    monitorThread.started.connect(timer.start)
    timer.timeout.connect(modem.monitor)

    trayIndicator = ModemIndicator(modem)
    modem.levelChanged.connect(
        trayIndicator.signalLevelChanged, QtCore.Qt.QueuedConnection)
    modem.statusChanged.connect(
        trayIndicator.statusChanged, QtCore.Qt.QueuedConnection)
    modem.signalParamsChanged.connect(
        trayIndicator.signalParamsChanged, QtCore.Qt.QueuedConnection)
    modem.unreadMessagesCountChanged.connect(
        trayIndicator.needNotify, QtCore.Qt.QueuedConnection)

    trayIndicator.show()
    monitorThread.start()

    return app.exec_()


def parseArgs():
    parser = argparse.ArgumentParser(
        description="hilink-tray - HiLink modems tray monitor",
        add_help=True)

    parser.add_argument(
        "-ip", "--ip",
        help="modem's ip adress",
        nargs="?", default="192.168.8.1")

    parser.add_argument(
        "-v", "--version",
        action="version", version="%(prog)s 4.0")

    return parser.parse_args()


if __name__ == '__main__':
    args = parseArgs()
    sys.exit(main(args.ip))
