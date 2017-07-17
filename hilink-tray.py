#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright: 2016, Wasylews
# Author: Wasylews
# License: MIT
import sys
import signal
import argparse
from PySide import QtGui
from hilink.tray import Tray


# load resources based on interpreter version
if sys.hexversion >= 0x3000000:
    import hilink.res3_rc
else:
    import hilink.res_rc


def main(ip, timeout):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray = Tray(ip, timeout)
    tray.show()

    return app.exec_()


def parseArgs():
    parser = argparse.ArgumentParser(
        description="hilink-tray - HiLink modems tray monitor",
        add_help=True)

    parser.add_argument(
        "-i", "--interval",
        help="send request each [INTERVAL] seconds",
        type=int,
        nargs="?")

    parser.add_argument(
        "-ip", "--ip",
        help="modem's ip address",
        nargs="?")

    parser.add_argument(
        "-v", "--version",
        action="version", version="%(prog)s 4.1")

    return parser.parse_args()


if __name__ == '__main__':
    args = parseArgs()
    sys.exit(main(args.ip, args.interval))
