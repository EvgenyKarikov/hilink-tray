#!/usr/bin/env python
# Copyright: 2016, Wasylews
# Author: Wasylews
# License: MIT

from __future__ import print_function
import sys
import signal
import socket
import res_rc
import argparse
from PySide import QtCore, QtGui
from PySide.phonon import Phonon
from xml.etree import ElementTree
from collections import OrderedDict

try:
    from urllib2 import build_opener, URLError
    from urlparse import urljoin
except ImportError:  # >= 3.x
    from urllib.request import build_opener
    from urllib.error import URLError
    from urllib.parse import urljoin


class ModemMonitor(QtCore.QThread):
    """ModemMonitor - class for monitoring modem parameters"""
    levelChanged = QtCore.Signal(int)
    statusChanged = QtCore.Signal(str, str)
    signalParamsChanged = QtCore.Signal(OrderedDict)
    unreadMessagesCountChanged = QtCore.Signal(int)

    def __init__(self, ip, timeout):
        super(ModemMonitor, self).__init__()

        self._url = "http://{}".format(ip)
        self._timeout = timeout
        self._running = True

    def stop(self):
        self._running = False

    def _getXml(self, opener, section):
        response = opener.open(urljoin(self._url, section), timeout=1)
        return ElementTree.fromstring(response.read())

    def getCookie(self, opener):
        """Get access token"""
        try:
            xml = self._getXml(opener, "/api/webserver/SesTokInfo")
        except URLError:
            return ""
        else:
            return xml.find("SesInfo").text

    def getSignalLevel(self, xml):
        return int(xml.find("SignalIcon").text)

    def getNetworkType(self, xml):
        types = {"0": "No Service", "1": "GSM", "2": "GPRS", "3": "EDGE",
                 "41": "WCDMA", "42": "HSDPA", "43": "HSUPA", "44": "HSPA",
                 "45": "HSPA+", "46": "DC-HSPA+", "101": "LTE"}
        return types[xml.find("CurrentNetworkTypeEx").text]

    def getStatus(self, xml):
        states = {"900": "Connecting", "901": "Connected",
                  "902": "Disconnected"}
        return states[xml.find("ConnectionStatus").text]

    def getOperator(self, xml):
        return xml.find("FullName").text

    def getSignalParams(self, xml):
        params = ["rssi", "rsrp", "rsrq", "rscp", "ecio", "sinr",
                  "cell_id", "pci"]
        values = OrderedDict()

        for key in params:
            values[key] = "{key}: {val}".format(key=key.upper(),
                                                val=xml.find(key).text)
        return values

    def getUnreadMessageCount(self, xml):
        """Get number of unreaded messages"""
        return int(xml.find("UnreadMessage").text)

    def monitorMessages(self, opener):
        """Monitor count of unreaded messages"""
        try:
            notifyXml = self._getXml(opener,
                                     "/api/monitoring/check-notifications")
            messageCount = self.getUnreadMessageCount(notifyXml)
        except:
            self.unreadMessagesCountChanged.emit(0)
        else:
            self.unreadMessagesCountChanged.emit(messageCount)

    def monitorStatus(self, opener):
        """Monitor connection status"""
        try:
            statusXml = self._getXml(opener, "/api/monitoring/status")
            plmnXml = self._getXml(opener, "/api/net/current-plmn")
        except:
            self.levelChanged.emit(0)
            self.statusChanged.emit("Disconnected", "")
        else:
            signalLevel = self.getSignalLevel(statusXml)
            self.levelChanged.emit(signalLevel)

            status = self.getStatus(statusXml)
            networkType = self.getNetworkType(statusXml)
            operator = self.getOperator(plmnXml)
            self.statusChanged.emit(status, "%s %s" % (operator, networkType))

    def monitorSignalParams(self, opener):
        """Monitor signal parameters"""
        try:
            signalXml = self._getXml(opener, "/api/device/signal")
        except:
            self.signalParamsChanged.emit({})
        else:
            params = self.getSignalParams(signalXml)
            self.signalParamsChanged.emit(params)

    def run(self):
        opener = build_opener()
        cookie = self.getCookie(opener)
        opener.addheaders.append(("Cookie", cookie))

        while self._running:
            self.monitorMessages(opener)
            self.monitorStatus(opener)
            self.monitorSignalParams(opener)

            self.sleep(self._timeout)


class ModemIndicator(QtGui.QSystemTrayIcon):
    """Simple tray indicator"""

    # is user already notified about unreaded messages or not
    _notified = False

    def __init__(self, monitor):
        super(ModemIndicator, self).__init__()
        self.signalLevelChanged(0)
        menu = self.createMenu()
        self.setContextMenu(menu)
        self._monitor = monitor

        self.player = Phonon.createPlayer(Phonon.MusicCategory)
        self.player.stateChanged.connect(self._playerLog)

    def createMenu(self):
        menu = QtGui.QMenu()
        quitAction = QtGui.QAction("Quit", menu)
        quitAction.triggered.connect(self.close)
        menu.addAction(quitAction)
        return menu

    def close(self):
        self.hide()
        self._monitor.stop()
        if not self._monitor.wait(5000):
            self._monitor.terminate()
            self._monitor.wait()
        QtGui.qApp.quit()

    def signalLevelChanged(self, level):
        if self._notified:
            return

        iconName = "://images/icons/icon_signal_00.png"
        if level in range(1, 6):
            iconName = "://images/icons/icon_signal_0{}.png".format(level)

        self.setIcon(QtGui.QIcon(iconName))

    def needNotify(self, messageCount):
        if not self._notified and messageCount > 0:
            iconName = "://images/icons/unread_message.gif"
            self.setIcon(QtGui.QIcon(iconName))
            self._playSound()
            self._notified = True
        else:
            self._notified = False

    def statusChanged(self, status, operator):
        if operator != "":
            self.setToolTip("%s\n%s" % (status, operator))
        else:
            self.setToolTip(status)

    def signalParamsChanged(self, params):
        tip = [self.toolTip()]
        for (key, value) in params.items():
            if value:
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

    monitor = ModemMonitor(ip, timeout)

    trayIndicator = ModemIndicator(monitor)
    monitor.levelChanged.connect(trayIndicator.signalLevelChanged)
    monitor.statusChanged.connect(trayIndicator.statusChanged)
    monitor.signalParamsChanged.connect(trayIndicator.signalParamsChanged)
    monitor.unreadMessagesCountChanged.connect(trayIndicator.needNotify)

    monitor.start()
    trayIndicator.show()

    return app.exec_()


def parseArgs():
    parser = argparse.ArgumentParser(
        description="hilink-tray - HiLink modems tray monitor",
        add_help=True,
        version="v3.0")

    parser.add_argument(
        "-t", "--timeout",
        help="check modem params each [TIMEOUT] seconds",
        type=int,
        nargs="?", default=5)

    parser.add_argument(
        "-ip", "--ip",
        help="modem's ip adress",
        nargs="?", default="192.168.8.1")

    return parser.parse_args()


if __name__ == '__main__':
    args = parseArgs()
    sys.exit(main(args.ip, args.timeout))
