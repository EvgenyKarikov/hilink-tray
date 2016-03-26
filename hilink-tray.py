#!/usr/bin/env python
# Copyright: 2016, Wasylews
# Author: Wasylews
# License: MIT

"""hilink-tray - display signal level for HiLink modems in a tray

Usage:
    hilink-tray.py [--timeout=N] [--ip=IP] [--log=LOGFILE]
    hilink-tray.py -h | --help
    hilink-tray.py -v | --version

Options:
    -t N --timeout=N  download icon each N seconds
                      [default: 5]
    --ip=IP           modem ip
                      [default: 192.168.8.1]
    --log=LOGFILE     write logs to this file
                      [default: err.log]
    -v --version      show version
    -h --help         show this message and exit
"""

from __future__ import print_function
import docopt
import sys
import logging
import os.path as path
from PySide import QtGui, QtCore
import lxml.etree as xmlp
from string import Formatter


class UnseenFormatter(Formatter):
    """String formatter for ''.format(), ignores empty values"""
    def __init__(self):
        Formatter.__init__(self)

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            try:
                return kwds[key]
            except KeyError:
                return ""
        else:
            Formatter.get_value(key, args, kwds)


class ModemSignalChecker(QtCore.QThread):
    """Class for monitoring some modem parameters and send to gui"""
    levelChanged = QtCore.Signal(int, str, str, str, str,
                                 str, str, str, str, str)

    def __init__(self, ip, timeout):
        super(ModemSignalChecker, self).__init__()
        self._ip = ip
        self._timeout = timeout
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        connectionStatus = ""
        level = -1
        operator = ""
        networkType = ""
        mode = ""
        rssi = ""
        rsrp = ""
        rsrq = ""
        sinr = ""
        rscp = ""
        ecio = ""
        while self._running:
            try:
                g = Grab()
                g.go('http://' + self._ip)
                g.go('http://' + self._ip + '/api/monitoring/status')
                status = xmlp.XML(g.response.body)
                level = int(status.xpath('/response/SignalIcon/text()')[0])
                networkType = int(
                    status.xpath('/response/CurrentNetworkTypeEx/text()')[0])
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
                connectionStatus = int(
                    status.xpath('/response/ConnectionStatus/text()')[0])
                if connectionStatus == 900:
                    connectionStatus = "Connecting"
                elif connectionStatus == 901:
                    connectionStatus = "Connected"
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
                connectionStatus = "?"
                mode = "?"
                rssi = "?"
                rsrp = "?"
                rsrq = "?"
                sinr = "?"
                rscp = "?"
                ecio = "?"

            self.levelChanged.emit(level, operator, networkType,
                                   connectionStatus, rssi, rsrp, rsrq,
                                   sinr, rscp, ecio)
            self.sleep(self._timeout)


class ModemIndicator(QtGui.QSystemTrayIcon):
    """Simple tray indicator"""
    def __init__(self, checker):
        super(ModemIndicator, self).__init__()
        menu = self.createMenu()
        self.setContextMenu(menu)
        self._checker = checker
        self.updateStatus(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1)

    def iconsPath(self):
        paths = ["icons", "/usr/share/pixmaps/hilink-tray/icons"]
        for iconsPath in paths:
            if not path.exists(iconsPath):
                logging.error("Cannot find icons folder")
                return ""
            else:
                return iconsPath

    def createMenu(self):
        menu = QtGui.QMenu()
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
        if level in range(1, 6):
            icon = "icon_signal_0{}.png".format(level)
        else:
            icon = "icon_signal_00.png"
        return path.join(self.iconsPath(), icon)

    def updateStatus(self, iconLevel, operator, networkType, connectionStatus,
                     rssi, rsrp, rsrq, sinr, rscp, ecio):
        values = {"operator": operator, "network": networkType,
                  "status": connectionStatus, "rssi": rssi,
                  "rsrp": rsrp, "rsrq": rsrq, "sinr": sinr,
                  "rscp": rscp, "ecio": ecio}

        tip = ("{operator} {network}\n{status}\nRSSI: {rssi}\nRSRP: {rsrp}\n"
               "RSRQ: {rsrq}\nSINR: {sinr}\nRSCP: {rscp}\nEc/Io: {ecio}")

        self.setToolTip(tip.format(**values).strip())
        icon = self.signalIcon(iconLevel)
        self.setIcon(QtGui.QIcon(icon))


def main(ip, timeout):
    app = QtGui.QApplication(sys.argv)
    checker = ModemSignalChecker(ip, timeout)
    tray = ModemIndicator(checker)
    checker.levelChanged.connect(tray.updateStatus)
    checker.start()
    tray.show()

    return app.exec_()

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version="v2.0")
    logFile = args["--log"]
    logging.basicConfig(format="%(levelname)-8s [%(asctime)s] %(message)s",
                        level=logging.ERROR,
                        filename=logFile)

    ip = args["--ip"]
    timeout = int(args["--timeout"])
    sys.exit(main(ip, timeout))
