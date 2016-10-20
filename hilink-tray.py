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


class ModemIndicator(QtGui.QSystemTrayIcon):
    """Simple tray indicator"""

    # store last message count
    _lastMessageCount = 0

    # is user notified or not
    _notified = False

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
        self.connectAction.triggered.connect(self._modem.connect_)
        menu.addAction(self.connectAction)

        self.disconnectAction = QtGui.QAction("Disconnect", menu)
        self.disconnectAction.triggered.connect(self._modem.disconnect)
        self.disconnectAction.setDisabled(True)
        menu.addAction(self.disconnectAction)

        self.rebootAction = QtGui.QAction("Reboot", menu)
        self.rebootAction.triggered.connect(self._modem.reboot)
        self.rebootAction.setDisabled(True)
        menu.addAction(self.rebootAction)

        menu.addSeparator()

        quitAction = QtGui.QAction("Quit", menu)
        quitAction.triggered.connect(self.quit)
        menu.addAction(quitAction)

        return menu

    def quit(self):
        self.hide()
        self._modem.finish()

    def signalLevelChanged(self, level):
        print(level)
        iconName = "://images/icons/icon_signal_00.png"
        if level in range(1, 6):
            iconName = "://images/icons/icon_signal_0{}.png".format(level)

        self.setIcon(QtGui.QIcon(iconName))

    def needNotify(self, messageCount):
        if messageCount > 0:
            if messageCount > self._lastMessageCount:
                self._playSound()
            iconName = "://images/icons/unread_message.gif"
            self.setIcon(QtGui.QIcon(iconName))

        self._lastMessageCount = messageCount

    def statusChanged(self, status, operator):
        if status == "No signal":
            self.connectAction.setDisabled(True)
            self.disconnectAction.setDisabled(True)
            self.rebootAction.setDisabled(True)
        else:
            self.rebootAction.setEnabled(True)
            if status == "Connected":
                self.connectAction.setDisabled(True)
                self.disconnectAction.setEnabled(True)
            elif status == "Disconnected":
                self.connectAction.setEnabled(True)
                self.disconnectAction.setDisabled(True)

        if operator != "":
            self.setToolTip("%s\n%s" % (status, operator))
        else:
            self.setToolTip(status)

    def signalParamsChanged(self, params):
        tip = [self.toolTip()]
        for value in params.values():
            tip.append(value)

        self.setToolTip("\n".join(tip))

    def _playSound(self):
        source = Phonon.MediaSource("://sounds/sounds/unread_message.wav")
        self.player.setCurrentSource(source)
        self.player.play()

    def _playerLog(self, newState, oldState):
        if newState == Phonon.ErrorState:
            print(self.player.errorString())


def main(ip, timeout):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)

    monitorThread = QtCore.QThread()
    modem = Modem(ip)
    modem.moveToThread(monitorThread)

    modem.finished.connect(monitorThread.quit)
    monitorThread.finished.connect(app.quit)

    timer = QtCore.QTimer()
    timer.setInterval(timeout)
    timer.moveToThread(monitorThread)

    monitorThread.started.connect(modem.start)
    timer.timeout.connect(modem.monitor)

    modem.started.connect(timer.start)
    modem.stopped.connect(timer.stop)

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
        "-t", "--timeout",
        help="check modem params each [TIMEOUT] seconds",
        type=int,
        nargs="?", default=5)

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
    sys.exit(main(args.ip, args.timeout * 1000))
