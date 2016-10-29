from __future__ import print_function
from PySide import QtCore
from xml.etree import ElementTree
from collections import OrderedDict

try:
    import hilink.res_rc
    from urllib2 import build_opener, URLError
    from urlparse import urljoin
except ImportError:  # >= 3.x
    import hilink.res3_rc
    from urllib.error import URLError
    from urllib.parse import urljoin


class Modem(QtCore.QObject):
    """Modem - class that represents HiLink modem"""
    levelChanged = QtCore.Signal(int)
    statusChanged = QtCore.Signal(str, str)
    signalParamsChanged = QtCore.Signal(OrderedDict)
    unreadMessagesCountChanged = QtCore.Signal(int)
    finished = QtCore.Signal()

    def __init__(self, ip):
        super(Modem, self).__init__()
        self._opener = build_opener()
        self._baseUrl = "http://{}".format(ip)

    def finish(self):
        self.finished.emit()

    def connect_(self):
        msg = """<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>1</dataswitch></request>"""

        self._post("/api/dialup/mobile-dataswitch", msg)

    def disconnect(self):
        msg = """<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>0</dataswitch></request>"""

        self._post("/api/dialup/mobile-dataswitch", msg)

    def reboot(self):
        msg = """<?xml version="1.0" encoding="UTF-8"?><request><Control>1</Control></request>"""
        self._post("/api/device/control", msg)

    def _post(self, section, msg):
        response = self._opener.open(urljoin(self._baseUrl, section),
                                     data=msg).read()
        print("[Response]", response)

    def _getXml(self, section):
        response = self._opener.open(urljoin(self._baseUrl, section),
                                     timeout=1).read()
        print("[Response]", response)
        return ElementTree.fromstring(response)

    def _getTokens(self):
        """Get access tokens"""
        try:
            xml = self._getXml("/api/webserver/SesTokInfo")
        except Exception as e:
            print("[Error]", e)
            return ("", "")
        else:
            return (xml.find("SesInfo").text, xml.find("TokInfo").text)

    def _updateTokens(self):
        session, postToken = self._getTokens()
        self._opener.addheaders = [("__RequestVerificationToken", postToken),
                                    ("Cookie", session)]

    def getSignalLevel(self, xml):
        return int(xml.find("SignalIcon").text)

    def getNetworkType(self, xml):
        types = {"0": "No Service", "1": "GSM", "2": "GPRS", "3": "EDGE",
                 "21": "IS-95A", "22": "IS-95B", "23": "CDMA 1X",
                 "24": "EV-DO Rev. 0", "25": "EV-DO Rev. A",
                 "26": "EV-DO Rev. A", "27": "Hybrid CDMA 1X",
                 "28": "Hybrid EV-DO Rev. 0", "29": "Hybrid EV-DO Rev. A",
                 "30": "Hybrid EV-DO Rev. A", "31": "eHPRD Rel. 0",
                 "32": "eHPRD Rel. A", "33": "eHPRD Rel. B",
                 "34": "Hybrid eHPRD Rel. 0", "35": "Hybrid eHPRD Rel. A",
                 "36": "Hybrid eHPRD Rel. B", "41": "WCDMA", "42": "HSDPA",
                 "43": "HSUPA", "44": "HSPA", "45": "HSPA+", "46": "DC-HSPA+",
                 "61": "TD-SCDMA", "62": "TD-HSDPA", "63": "TD-HSUPA",
                 "64": "TD-HSPA", "65": "TD-HSPA+", "81": "802.16e",
                 "101": "LTE"}
        return types[xml.find("CurrentNetworkTypeEx").text]

    def getStatus(self, xml):
        states = {"900": "Connecting", "901": "Connected",
                  "902": "Disconnected", "903": "Disconnecting"}
        return states[xml.find("ConnectionStatus").text]

    def getOperator(self, xml):
        shortName = xml.find("ShortName")
        if shortName is not None:
            return shortName.text
        else:
            fullName = xml.find("FullName")
            if fullName is not None:
                return fullName.text
        return ""

    def getSignalParams(self, xml):
        params = ["rssi", "rsrp", "rsrq", "rscp", "ecio", "sinr",
                  "cell_id", "pci"]
        values = OrderedDict()

        for key in params:
            value = xml.find(key).text
            if value:
                values[key] = "{key}: {val}".format(key=key.upper(),
                                                    val=value)
        return values

    def getUnreadMessageCount(self, xml):
        """Get number of unreaded messages"""
        return int(xml.find("UnreadMessage").text)

    def monitorMessages(self):
        """Monitor count of unreaded messages"""
        try:
            notifyXml = self._getXml("/api/monitoring/check-notifications")
            messageCount = self.getUnreadMessageCount(notifyXml)
        except Exception as e:
            self.unreadMessagesCountChanged.emit(0)
            print("[Error]", e)
        else:
            self.unreadMessagesCountChanged.emit(messageCount)

    def monitorStatus(self):
        """Monitor connection status"""
        try:
            statusXml = self._getXml("/api/monitoring/status")
            plmnXml = self._getXml("/api/net/current-plmn")
        except URLError as e:
            self.levelChanged.emit(0)
            print("[Error]", e)
            self.statusChanged.emit("No HiLink Detected", "")
        else:
            signalLevel = self.getSignalLevel(statusXml)
            self.levelChanged.emit(signalLevel)

            status = self.getStatus(statusXml)
            networkType = self.getNetworkType(statusXml)
            operator = self.getOperator(plmnXml)

            # fix space if we don't have op name
            op = networkType
            if operator:
                op = "%s %s" % (operator, networkType)
            self.statusChanged.emit(status, op)

    def monitorSignalParams(self):
        """Monitor signal parameters"""
        try:
            signalXml = self._getXml("/api/device/signal")
        except Exception as e:
            self.signalParamsChanged.emit({})
            print("[Error]", e)
        else:
            params = self.getSignalParams(signalXml)
            self.signalParamsChanged.emit(params)

    def monitor(self):
        self._updateTokens()
        self.monitorMessages()
        self.monitorStatus()
        self.monitorSignalParams()
