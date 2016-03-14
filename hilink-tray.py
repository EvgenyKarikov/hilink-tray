#!/usr/bin/env python

""""Usage: hilink-tray --timeout=N IP


Arguments:
    IP  modem ip

Options:
    -t N --timeout=N  download icon each N seconds
"""

from __future__ import print_function
import docopt
import sys
import telnetlib
import re
import logging
import os.path as path
from PySide import QtGui, QtCore

logging.basicConfig(format="%(levelname)-8s [%(asctime)s] %(message)s",
                    level=logging.ERROR,
                    filename="/var/log/hilink-tray/err.log")


class ModemSignalChecker(QtCore.QThread):
    levelChanged = QtCore.Signal(int)

    def __init__(self, ip, timeout):
        super(ModemSignalChecker, self).__init__()
        self._ip = ip
        self._timeout = timeout
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        level = -1
        while self._running:
            try:
                conn = telnetlib.Telnet(self._ip, timeout=1)
                conn.write("atc AT+CSQ\n")
                answer = conn.read_until("OK")
                result = re.search(r"\+CSQ: (.+),", answer)
                level = int(result.group(1))
            except Exception as e:
                logging.error(e)

            self.levelChanged.emit(level)
            self.sleep(self._timeout)


class ModemIndicator(QtGui.QSystemTrayIcon):

    def __init__(self, checker):
        super(ModemIndicator, self).__init__()
        menu = self.createMenu()
        self.setContextMenu(menu)
        self._checker = checker
        self.updateIcon(-1)

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
        iconPath = "/usr/share/pixmaps/hilink-tray/icons"
        if -70 <= level <= -45:
            icon = path.join(iconPath, "icon_signal_05.png")
        elif -90 <= level <= -71:
            icon = path.join(iconPath, "icon_signal_04.png")
        elif -100 <= level <= -91:
            icon = path.join(iconPath, "icon_signal_03.png")
        elif -120 <= level <= -101:
            icon = path.join(iconPath, "icon_signal_02.png")
        elif -130 <= level <= -121:
            icon = path.join(iconPath, "icon_signal_01.png")
        else:
            icon = path.join(iconPath, "icon_signal_00.png")
        return icon

    def updateIcon(self, signalLevel):
        db = -113 + signalLevel * 2

        toolTip = "Signal: %d db" % db if signalLevel > -1 else "No signal"
        self.setToolTip(toolTip)

        icon = self.signalIcon(db)
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
    sys.exit(main(args["IP"], int(args["--timeout"])))
