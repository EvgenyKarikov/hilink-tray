#!/usr/bin/env python

""""Usage: hilink-tray [--timeout=N] [IP]


Arguments:
    IP  modem ip

Options:
    -t N --timeout=N  download icon each N seconds
"""

from __future__ import print_function
import docopt
import sys
import logging
import os.path as path
from PySide import QtGui, QtCore
from grab import Grab
import lxml.etree as xmlp

try:
    logTry = open('err.log')
except IOError as e:
    log = "/var/log/hilink-tray/err.log"
else:
    log = "err.log"
logging.basicConfig(format="%(levelname)-8s [%(asctime)s] %(message)s",
                    level=logging.ERROR,
                    filename=log)


class ModemSignalChecker(QtCore.QThread):
    levelChanged = QtCore.Signal(int, str, str, str, str, str, str, str, str, str)

    def __init__(self, ip, timeout):
        super(ModemSignalChecker, self).__init__()
        self._ip = ip
        self._timeout = timeout
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        connectionStatus = "?"
        level = -1
        operator = "?"
        networkType = "?"
        mode = "?"
        rssi = "?"
        rsrp = "?"
        rsrq = "?"
        sinr = "?"
        rscp = "?"
        ecio = "?"
        while self._running:
            try:
                g = Grab()
                g.go('http://' + self._ip)
                g.go('http://' + self._ip + '/api/monitoring/status')
                status = xmlp.XML(g.response.body)
                level = int(status.xpath('/response/SignalIcon/text()')[0])
                networkType = int(status.xpath('/response/CurrentNetworkTypeEx/text()')[0])
                if networkType == 0:
                    networkType = "No Service"
                elif networkType == 1:
                    networkType = "GSM"
                elif networkType == 2:
                    networkType = "GPRS"
                elif networkType == 3:
                    networkType = "EDGE"
                elif networkType == 41:
                    networkType = "WCDMA"
                elif networkType == 42:
                    networkType = "HSDPA"
                elif networkType == 43:
                    networkType = "HSUPA"
                elif networkType == 44:
                    networkType = "HSPA"
                elif networkType == 45:
                    networkType = "HSPA+"
                elif networkType == 46:
                    networkType = "DC-HSPA+"
                elif networkType == 101:
                    networkType = "LTE"
                else:
                    networkType = ""
                connectionStatus = int(status.xpath('/response/ConnectionStatus/text()')[0])
                if connectionStatus == 900:
                	connectionStatus = "Connecting"
                elif connectionStatus == 901:
                	connectionStatus ="Connected"
                elif connectionStatus == 902:
                	connectionStatus = "Disconnected"
                else:
                	connectionStatus = "?"
                g.go('http://' + self._ip + '/api/net/current-plmn')
                currentPlmn = xmlp.XML(g.response.body)
                operator = currentPlmn.xpath('/response/FullName/text()')[0]
                try:
                    operator
                except NameError:
                    operator = "?"
                g.go('http://' + self._ip + '/api/device/signal')
                signal = xmlp.XML(g.response.body)
                mode = int(signal.xpath('/response/mode/text()')[0])
                if mode == 7:
                    rssi = signal.xpath('/response/rssi/text()')[0]
                    rsrp = signal.xpath('/response/rsrp/text()')[0]
                    rsrq = signal.xpath('/response/rsrq/text()')[0]
                    sinr = signal.xpath('/response/sinr/text()')[0]
                    rscp = '?'
                    ecio = '?'
                elif mode == 0:
                    rssi = '?'
                    rsrp = '?'
                    rsrq = '?'
                    sinr = '?'
                    rscp = '?'
                    ecio = '?'
                else:
                    rssi = signal.xpath('/response/rssi/text()')[0]
                    rsrp = '?'
                    rsrq = '?'
                    sinr = '?'
                    rscp = signal.xpath('/response/rscp/text()')[0]
                    ecio = signal.xpath('/response/ecio/text()')[0]
            except Exception as e:
                logging.error(e)
                level = -1
                operator = "?"
                networkType = ""
                connectionStatus ="?"
                mode = "?"
                rssi = "?"
                rsrp = "?"
                rsrq = "?"
                sinr = "?"
                rscp = "?"
                ecio = "?"

            self.levelChanged.emit(level, operator, networkType, connectionStatus, rssi, rsrp, rsrq, sinr, rscp, ecio)
            self.sleep(self._timeout)


class ModemIndicator(QtGui.QSystemTrayIcon):

    def __init__(self, checker):
        super(ModemIndicator, self).__init__()
        menu = self.createMenu()
        self.setContextMenu(menu)
        self._checker = checker
        self.updateIcon(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1)

    def disconnect(self):
        g = Grab()
        g.go('http://' + ip)
        g.setup(post='<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>0</dataswitch></request>')
        g.go('http://' + ip + '/api/dialup/mobile-dataswitch')

    def createMenu(self):
        menu = QtGui.QMenu()
        disconnectAction = QtGui.QAction("Disconnect", menu)
        disconnectAction.triggered.connect(self.disconnect)
        menu.addAction(disconnectAction)
        quitAction = QtGui.QAction("Quit", menu)
        quitAction.triggered.connect(self.close)
        menu.addAction(quitAction)
        return menu

    def close(self):
        self.hide()
        self._checker.stop()
        self._checker.wait()
        QtGui.qApp.quit()

    def signalIcon(self, level):
        if path.exists("icons"):
            iconPath = "icons"
        else:
            iconPath = "/usr/share/pixmaps/hilink-tray/icons"
        if level == 5:
            icon = path.join(iconPath, "icon_signal_05.png")
        elif level == 4:
            icon = path.join(iconPath, "icon_signal_04.png")
        elif level == 3:
            icon = path.join(iconPath, "icon_signal_03.png")
        elif level == 2:
            icon = path.join(iconPath, "icon_signal_02.png")
        elif level == 1:
            icon = path.join(iconPath, "icon_signal_01.png")
        else:
            icon = path.join(iconPath, "icon_signal_00.png")
        return icon

    def updateIcon(self, iconLevel, operator, networkType, connectionStatus, rssi, rsrp, rsrq, sinr, rscp, ecio):
        toolTip = str(operator) + " " + str(networkType) + "\n" + str(connectionStatus) + "\n" + "RSSI: " + str(rssi) + "\n" + "RSRP: " + str(rsrp) + "\n" + "RSRQ: " + str(rsrq) + "\n" + "SINR: " + str(sinr) + "\n" + "RSCP: " + str(rscp) + "\n" + "Ec/Io: " + str(ecio)
        self.setToolTip(toolTip)
        icon = self.signalIcon(iconLevel)
        self.setIcon(QtGui.QIcon(icon))


def main(ip, timeout):
    app = QtGui.QApplication(sys.argv)
    checker = ModemSignalChecker(ip, timeout)
    tray = ModemIndicator(checker)
    checker.levelChanged.connect(tray.updateIcon)
    checker.start()
    tray.show()

    return app.exec_()

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    if str(args["IP"]) == "None":
        ip = "192.168.8.1"
    else:
        ip = args["IP"]
    if str(args["--timeout"]) == "None":
        timeout = "5"
    else:
        timeout = args["--timeout"]
    sys.exit(main(ip, int(timeout)))
